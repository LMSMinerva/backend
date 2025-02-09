from django.urls import path
from content.views import ContentDetailView, ContentListView

urlpatterns = [
    path("content/", ContentListView.as_view(), name="content_list"),
    path(
        "content/<uuid:id>/",
        ContentDetailView.as_view(),
        name="content_detail",
    ),
]
