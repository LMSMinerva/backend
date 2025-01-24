from django.urls import path
from course_category.views import CourseCategoryListView, CourseCategoryDetailView

urlpatterns = [
    path(
        "course_category/",
        CourseCategoryListView.as_view(),
        name="course_category_list_create",
    ),
    path(
        "course_category/<uuid:id>/",
        CourseCategoryDetailView.as_view(),
        name="course_category_detail_update_delete",
    ),
]
