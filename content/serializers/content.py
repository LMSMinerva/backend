from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers
from content.models.content import Content
import json


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = "__all__"

    def validate(self, data):
        """
        Validación personalizada para 'metadata' y 'body'.
        """

        metadata = data.get("metadata")
        body = data.get("body")
        content_type = data.get("content_type")

        # Validar body para los tipos de contenido que deben ser URLs
        if content_type and content_type.name in ["video", "pdf", "codigo"]:
            validator = URLValidator()
            try:
                validator(body)
            except ValidationError:
                raise serializers.ValidationError({"body": "Debe ser una URL válida."})

            # Validar que metadata para 'codigo' tenga la clave "lenguajes" y sea una lista de strings
            if content_type.name == "codigo":
                if "lenguajes" not in metadata:
                    raise serializers.ValidationError(
                        {"metadata": "Debe contener la clave 'lenguajes'."}
                    )

                if not isinstance(metadata["lenguajes"], list) or not all(
                    isinstance(lang, str) for lang in metadata["lenguajes"]
                ):
                    raise serializers.ValidationError(
                        {"metadata": "'lenguajes' debe ser una lista de strings."}
                    )

        return data
