from decimal import Decimal
import uuid
from django.db import models
from django.contrib.auth.models import User
from content.models.content import Content
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count


class ContentInteraction(models.Model):
    """
    Model for Content Interaction

    Attributes:
        id (uuid): Unique identifier for the content interaction.
        user (User): Foreign key to the user who interacted with the content.
        content (Content): Foreign key to the associated content.
        completed (bool): Indicates whether the user completed the content.
        rating (int): Optional rating given by the user to the content (e.g., 1 to 5).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    completed = models.BooleanField(null=False)
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5",
    )

    class Meta:
        unique_together = ("user", "content")

    def __str__(self):
        return f"{self.user.username} - {self.content.title} - {'Completed' if self.completed else 'Incomplete'}"

    def update_content_metrics(self, content=None):
        """Recalculate the content's average rating and review count."""
        content = content or self.content
        interactions = ContentInteraction.objects.filter(content=content)
        content.reviews = interactions.count()
        content.rating = Decimal(
            round(
                interactions.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0, 2
            )
        )
        content.save()

    def save(self, *args, **kwargs):
        """Override save to update Content's rating and reviews."""
        super().save(*args, **kwargs)
        self.update_content_metrics()

    def delete(self, *args, **kwargs):
        """Override delete to update Content's rating and reviews."""
        content = self.content
        super().delete(*args, **kwargs)
        self.update_content_metrics(content)
