from django.urls import path
from .views.views import CourseView, CourseDetailView

urlpatterns = [
    path("courses/", CourseView.as_view(), name="course_list_create"),
    path(
        "courses/<uuid:id>/",
        CourseDetailView.as_view(),
        name="course_detail_update_delete",
    ),
]
