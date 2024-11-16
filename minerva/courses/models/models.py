from django.db import models

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    alias = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    visibility = models.BooleanField(default=True)
    description = models.TextField()
    format = models.CharField(max_length=50)
    creation_date = models.DateField()
    id_instructor = models.TextField()
    total_students_enrolled = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    

