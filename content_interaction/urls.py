from django.urls import path
from content_interaction.views import (
    ContentInteractionDetailView,
    ContentInteractionListView,
)

urlpatterns = [
    path(
        "content_interaction/",
        ContentInteractionListView.as_view(),
        name="content_interaction_list",
    ),
    path(
        "content_interaction/<uuid:id>/",
        ContentInteractionDetailView.as_view(),
        name="content_interaction_detail",
    ),
]
