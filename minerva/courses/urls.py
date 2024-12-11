from django.urls import path
from courses.views import CourseView, CourseDetailViewById, CourseDetailViewBySlug

urlpatterns = [
    path("courses/", CourseView.as_view(), name="course_list_create"),
    path(
        "courses/<uuid:id>/",
        CourseDetailViewById.as_view(),
        name="course_detail_by_id",
    ),
    path(
        "courses/<slug:alias>/",
        CourseDetailViewBySlug.as_view(),
        name="course_detail_by_slug",
    ),
]
