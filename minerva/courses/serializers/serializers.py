from rest_framework import serializers
from ..models.models import Course
from course_category.models.models import CourseCategory
from institution.models.models import Institution

class CourseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=CourseCategory.objects.all())
    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all())
    class Meta:
        model = Course
        fields = ['id', 'category', 'institution', 'name', 'alias', 'active', 'description', 'creation_date', 'last_update', 'modules_count']
