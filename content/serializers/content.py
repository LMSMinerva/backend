import json
import re
import uuid
import random
import ast
from rest_framework import serializers
from content.models.content import Content
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .utils import validate_seleccion_body

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = "__all__"

    def validate(self, data):
        """Validación personalizada para 'metadata' y 'body'."""
        metadata = data.get("metadata")
        body = data.get("body")
        content_type = data.get("content_type")

        # Validar que los tipos de contenido `video`, `pdf` y `codigo` tengan una URL válida en `body`
        if content_type and content_type.name in ["video", "pdf", "codigo"]:
            validator = URLValidator()
            try:
                validator(body)
            except ValidationError:
                raise serializers.ValidationError({"body": "Debe ser una URL válida."})

            # Validar que `metadata` en `codigo` contenga la clave "lenguajes"
            if content_type.name == "codigo":
                if not isinstance(metadata, dict) or "lenguajes" not in metadata:
                    raise serializers.ValidationError(
                        {"metadata": "Debe contener la clave 'lenguajes'."}
                    )
                if not isinstance(metadata["lenguajes"], list) or not all(
                    isinstance(lang, str) for lang in metadata["lenguajes"]
                ):
                    raise serializers.ValidationError(
                        {"metadata": "'lenguajes' debe ser una lista de strings."}
                    )

        # Validar `seleccion`
        if content_type and content_type.name == "seleccion":
            # Usar la función de validación específica para seleccion
            is_valid, error_message = validate_seleccion_body(body)
            if not is_valid:
                raise serializers.ValidationError({"body": error_message})

        # Asegurar que las respuestas tengan IDs únicos y valores correctos de boolean
            new_respuestas = []
            for resp in body["respuestas"]:
                if len(resp) == 2:
                    # Agregar ID si no existe
                    resp_id = str(uuid.uuid4())
                    new_respuestas.append([resp_id, resp[0], resp[1]])
                else:
                    # Asegurar que el tercer elemento sea boolean
                    new_respuestas.append([resp[0], resp[1], bool(resp[2])])

            body["respuestas"] = new_respuestas
            
        return data