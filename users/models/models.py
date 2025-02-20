from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Make it nullable
    picture = models.URLField(max_length=500, blank=True)
    given_name = models.CharField(max_length=100, blank=True)
    family_name = models.CharField(max_length=100, blank=True)
    locale = models.CharField(max_length=10, blank=True)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=20, blank=True)
    birthday_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

