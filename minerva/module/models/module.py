import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Module(models.Model):
    """
    Model for Modules

    Attributes:
        id (uuid): Unique identifier for the module
        id_course (uuid): Foreign key to the associated course
        name (str): Name of the module
        description (str): Description of the module
        order (int): The order in which the module appears in the course (automatically assigned)
        instructional_items (int): Number of instructional elements in the module
        assessment_items (int): Number of assessment elements in the module
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_course = models.ForeignKey(
        "course.Course", on_delete=models.CASCADE, related_name="course_modules"
    )
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=512, blank=True, null=True)
    order = models.IntegerField(default=0, null=True, blank=True)
    instructional_items = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )
    assessment_items = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(64)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["id_course", "order"], name="unique_order_per_course"
            )
        ]

    def save(self, *args, **kwargs):
        """
        Assigns 'order' and updates the module count for the course.

        Necessary to keep the module order consistent and update the course's module count.
        """
        if not self.order:
            self.order = self.id_course.modules + 1
            self.id_course.modules += 1
            self.id_course.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Updates the module count and reorders the remaining modules after deletion.
        Necessary to maintain an accurate module count and ensure proper order sequence.
        """
        course = self.id_course
        module_order = self.order
        course.modules -= 1
        course.save()
        super().delete(*args, **kwargs)
        Module.objects.filter(id_course=course, order__gt=module_order).update(
            order=models.F("order") - 1
        )

    def __str__(self):
        return self.name
