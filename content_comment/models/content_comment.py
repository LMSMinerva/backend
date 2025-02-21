from django.db import models
import uuid
from django.contrib.auth.models import User
from content.models import Content


class ContentComment(models.Model):
    """
    Model for Content Comment

    Attributes:
        id (uuid): Unique identifier for the comment.
        user (User): The user who made the comment.
        content (Content): The content associated with the comment.
        parent_comment (ContentComment): Optional. If set, indicates this is a reply.
        comment (str): The actual comment text.
        comment_date (datetime): When the comment was made.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    comment = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.comment[:30]}"

    def get_replies(self):
        """Return all replies to this comment."""
        return self.replies.all()

    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent_comment is not None

    def save(self, *args, **kwargs):
        """Override save to increment comment count on Content."""
        is_new = self._state.adding  # Checks if it's a new instance
        super().save(*args, **kwargs)
        if is_new:
            self.content.comments = models.F("comments") + 1
            self.content.save(update_fields=["comments"])

    def delete(self, *args, **kwargs):
        """Override delete to decrement comment count on Content."""
        super().delete(*args, **kwargs)
        self.content.comments = models.F("comments") - 1
        self.content.save(update_fields=["comments"])
