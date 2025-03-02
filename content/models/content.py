import json
import uuid
import random
from django.db import models
from django.core.exceptions import ValidationError
from module.models.module import Module


class Content(models.Model):
    """
    Model for Content

    Attributes:
        id (uuid): Unique identifier for the content
        module (Module): Foreign key to the associated module
        content_type (str): Type of content (e.g., video, text, quiz)
        name (str): Name of the content
        description (str): Description of the content
        order (int): Order of the content within the module
        reviews (int): Number of reviews
        rating (float): Average rating
        comments (int): Number of comments
        metadata (json): Stores specific metadata depending on the content type
        body (json): Stores structured content (e.g., URLs for media or JSON for "selección")
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="contents"
    )
    content_type = models.ForeignKey(
        "content_category.ContentCategory", on_delete=models.PROTECT
    )
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(max_length=512, blank=True, null=True)
    order = models.PositiveIntegerField(blank=True, default=0)
    reviews = models.PositiveIntegerField(default=0, blank=True)
    comments = models.PositiveIntegerField(default=0, blank=True)
    rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(blank=True, null=True)
    body = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.module.name} - {self.name}"

    def clean(self):
        """Validates that `body` and `metadata` have the correct format based on `content_type`."""
        if self.content_type.name in ["codigo", "pdf", "video"]:
            if not isinstance(self.body, str) or not self.body.startswith(
                ("http://", "https://")
            ):
                raise ValidationError({"body": "Debe ser una URL válida."})

            if self.content_type.name in ["pdf", "video"]:
                if not isinstance(self.metadata, (int, float)):
                    raise ValidationError({"metadata": "Debe ser un número."})

            if self.content_type.name == "codigo":
                if (
                    not isinstance(self.metadata, dict)
                    or "lenguajes" not in self.metadata
                ):
                    raise ValidationError(
                        {"metadata": "Debe contener la clave 'lenguajes'."}
                    )
                if not isinstance(self.metadata["lenguajes"], list) or not all(
                    isinstance(lang, str) for lang in self.metadata["lenguajes"]
                ):
                    raise ValidationError(
                        {"metadata": "'lenguajes' debe ser una lista de strings."}
                    )

        elif self.content_type.name == "seleccion":
            # Validar que `body` sea un JSON con las claves esperadas
            required_keys = {"variables", "enunciado", "respuestas"}
            if not isinstance(self.body, dict) or not required_keys.issubset(
                self.body.keys()
            ):
                raise ValidationError(
                    {
                        "body": "Debe contener las claves 'variables', 'enunciado' y 'respuestas'."
                    }
                )

            # Validate `metadata` is a number
            if not isinstance(self.metadata, (int, float)):
                raise ValidationError({"metadata": "Debe ser un número."})

    def update_module_items(self):
        """Update instructional_items and assessment_items in module."""
        instructional_types = ["pdf", "video"]
        assessment_types = ["seleccion", "codigo"]

        module = self.module
        course = module.course

        module.instructional_items = module.contents.filter(
            content_type__name__in=instructional_types
        ).count()
        module.assessment_items = module.contents.filter(
            content_type__name__in=assessment_types
        ).count()

        module.save(update_fields=["instructional_items", "assessment_items"])
        course.assessment_items = (
            course.modules.aggregate(total=models.Sum("assessment_items"))["total"] or 0
        )
        course.save(update_fields=["assessment_items"])

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
        self.update_module_items()

    def delete(self, *args, **kwargs):
        """
        Before deleting, adjust the order of remaining contents.
        """
        super().delete(*args, **kwargs)
        self.update_module_items()
        module_contents = Content.objects.filter(module=self.module).order_by("order")
        for index, content in enumerate(module_contents):
            content.order = index + 1
            content.save()
