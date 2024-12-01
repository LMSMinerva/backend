from rest_framework import serializers
from ..models.models import CourseCategory

class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'name']