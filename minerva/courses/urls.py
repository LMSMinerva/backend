from django.urls import path
from .views.views import CourseView

urlpatterns = [
    path('courses/', CourseView.as_view(), name='course_list_create'),
    path('courses/<int:pk>/', CourseView.as_view(), name='course_detail_update_delete'),
]