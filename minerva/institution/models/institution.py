from django.db import models
import uuid


class Institution(models.Model):
    """
    Model for representing an Institution.

    Attributes:
        id (uuid): A unique identifier for the institution.
        name (str): The full name of the institution.
        description (str): A brief description of the institution.
        url (str): The URL to the institution's website.
        image (str): A URL or path to an image representing the institution.
        icon (str): A URL or path to the institution's emblem or shield icon.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    image = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)

    def __str__(self):
        return self.name
