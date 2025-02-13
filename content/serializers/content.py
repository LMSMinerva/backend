from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers
import json
from content.models.content import Content


class ContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Content
        fields = "__all__"

    def validate_body(self, value):
        """
        Validación personalizada para el campo 'body' basada en el valor de 'metadata'.
        """
        metadata = self.initial_data.get("metadata", "").lower()

        if metadata in ["pdf", "video"]:
            validator = URLValidator()
            try:
                validator(value)
            except ValidationError:
                raise serializers.ValidationError("Debe ser una URL válida.")

        elif metadata in ["codigo", "seleccion"]:
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Debe ser un JSON válido.")

        return value
