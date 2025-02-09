import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from course.models.course import Course


class Module(models.Model):
    """
    Model for Modules

    Attributes:
        id (uuid): Unique identifier for the module
        course (uuid): Foreign key to the associated course
        name (str): Name of the module
        description (str): Description of the module
        order (int): The order in which the module appears in the course (automatically assigned)
        instructional_items (int): Number of instructional elements in the module
        assessment_items (int): Number of assessment elements in the module
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=512, blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, default=0)
    instructional_items = models.PositiveIntegerField(
        blank=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(64)]
    )
    assessment_items = models.PositiveIntegerField(
        blank=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(64)]
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.name} - {self.name}"

    def save(self, *args, **kwargs):
        """
        Auto-assigns an order to the module if it's new,
        ensuring the order is consecutive within the course.
        """
        if self.order == 0:
            last_order = Module.objects.filter(course=self.course).aggregate(
                models.Max("order")
            )["order__max"]
            self.order = (last_order or 0) + 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Before deleting, adjust the order of remaining modules.
        """
        super().delete(*args, **kwargs)
        course_modules = Module.objects.filter(course=self.course).order_by("order")
        for index, module in enumerate(course_modules):
            module.order = index + 1
            module.save()

    @property
    def ordered_contents(self):
        """Returns the contents ordered by 'order' field."""
        return self.contents.order_by("order")
