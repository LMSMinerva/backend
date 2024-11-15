from rest_framework import serializers
from ..models.models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'alias', 'category', 'visibility', 'description', 'format', 'creation_date', 'id_instructor', 'total_students_enrolled']