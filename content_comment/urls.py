from django.urls import path

from content_comment.views.content_comment import (
    CommentRepliesView,
    ContentCommentDetailView,
    ContentCommentListView,
)

urlpatterns = [
    path("comments/", ContentCommentListView.as_view(), name="content_comment_list"),
    path(
        "comments/<uuid:id>/",
        ContentCommentDetailView.as_view(),
        name="content_comment_detail",
    ),
    path(
        "comments/<uuid:id>/replies/",
        CommentRepliesView.as_view(),
        name="comment_replies",
    ),
]
