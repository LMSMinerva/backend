import uuid
from django.db import models

from module.models.module import Module


class Content(models.Model):
    """
    Model for Content

    Attributes:
        id (uuid): Unique identifier for the content
        content (content): Foreign key to the associated content
        content_type (str): Type of content (e.g., video, text, quiz)
        name (str): Name of the content
        description (str): Description of the content
        order (int): Order of the content within the content
        reviews (int): Number of reviews
        rating (float): Average rating
        comments (int): Number of comments
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="contents"
    )
    content_type = models.ForeignKey(
        "content_category.ContentCategory", on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(max_length=512, blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, default=0)
    reviews = models.PositiveIntegerField(default=0, blank=True)
    comments = models.PositiveIntegerField(default=0, blank=True)
    rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.content.name} - {self.name}"

    def save(self, *args, **kwargs):
        """
        Auto-assigns an order to the content if it's new,
        ensuring the order is consecutive within the content.
        """
        if self.order == 0:
            last_order = Content.objects.filter(module=self.module).aggregate(
                models.Max("order")
            )["order__max"]
            self.order = (last_order or 0) + 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Before deleting, adjust the order of remaining contents.
        """
        super().delete(*args, **kwargs)
        module_contents = Content.objects.filter(module=self.module).order_by("order")
        for index, content in enumerate(module_contents):
            content.order = index + 1
            content.save()
