from django.db import models
import uuid
class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    visibility = models.BooleanField(default=True)
    description = models.TextField()
    creation_date = models.DateField()

    def __str__(self):
        return self.name
    

