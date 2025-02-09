from rest_framework import serializers
from content_category.models import ContentCategory


class ContentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentCategory
        fields = "__all__"
