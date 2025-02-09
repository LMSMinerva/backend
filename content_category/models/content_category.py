from django.db import models
import uuid


class ContentCategory(models.Model):
    """
    Model for ContentCategory

    Attributes:
        id (uuid): Unique identifier for the category
        name (str): Name complete of category
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
