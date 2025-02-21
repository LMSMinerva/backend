"""
init content for content_interaction view
"""

from content_comment.views.content_comment import (
    ContentCommentListView,
    ContentCommentDetailView,
    CommentRepliesView,
)

__all__ = ["ContentCommentListView", "ContentCommentDetailView", "CommentRepliesView"]
