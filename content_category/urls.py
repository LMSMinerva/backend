from django.urls import path
from content_category.views import ContentCategoryListView, ContentCategoryDetailView

urlpatterns = [
    path(
        "content_category/",
        ContentCategoryListView.as_view(),
        name="content_category_list_create",
    ),
    path(
        "content_category/<uuid:id>/",
        ContentCategoryDetailView.as_view(),
        name="content_category_detail_update_delete",
    ),
]
