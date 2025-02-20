from rest_framework import serializers
from content_interaction.models.content_interaction import ContentInteraction


class ContentInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentInteraction
        fields = "__all__"
