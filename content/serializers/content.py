from rest_framework import serializers

from content.models.content import Content


class ContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Content
        fields = "__all__"
