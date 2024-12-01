from django.db import models
import uuid


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        "course_category.CourseCategory", on_delete=models.SET_NULL, null=True
    )
    institution = models.ForeignKey(
        "institution.Institution", on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    description = models.TextField()
    creation_date = models.DateField()
    last_update = models.DateField()
    modules_count = models.IntegerField()

    def __str__(self):
        return self.name
