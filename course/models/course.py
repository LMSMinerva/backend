from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
import uuid


class Course(models.Model):
    """
    Model for Courses

    Attributes:
        id (uuid): Unique identifier for the course
        name (str): Name complete of course
        alias (str): A short form of call a course
        description (str): A description about the course
        creation_date (date): Date of creation of the course
        last_update (date): Date of the last update
        modules (int): count the number of modules
        active (bool): true if the course is active
        assessment_items (int): elemnts of evaluate
        reviews (int): The number of reviews
        comments (int): The number of comments
        rating (float): The mean appraisement of the course
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        "course_category.CourseCategory", on_delete=models.SET_NULL, null=True
    )
    institution = models.ForeignKey(
        "institution.Institution", on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(max_length=64, unique=True)
    alias = models.CharField(
        max_length=16,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9_-]+$",
                message="Alias must contain only lowercase letters, numbers, underscores (_), or hyphens (-), without spaces.",
            )
        ],
    )
    active = models.BooleanField(default=False, blank=True)
    description = models.TextField(max_length=512, null=True, blank=True)
    creation_date = models.DateField(auto_now_add=True, blank=True)
    last_update = models.DateField(auto_now=True, blank=True)
    modules = models.IntegerField(
        default=0,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(16)],
    )
    assessment_items = models.PositiveIntegerField(default=0, blank=True)
    reviews = models.PositiveIntegerField(default=0, blank=True)
    comments = models.PositiveIntegerField(default=0, blank=True)
    rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
