import json
import re
import uuid
import random
import ast
from rest_framework import serializers
from content.models.content import Content
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


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
            required_keys = {"variables", "enunciado", "respuestas"}
            if not isinstance(body, dict) or not required_keys.issubset(body.keys()):
                raise serializers.ValidationError(
                    {
                        "body": "Debe contener las claves 'variables', 'enunciado' y 'respuestas'."
                    }
                )

            # Ejecutar y validar variables
            variables_code = body["variables"]
            context = {"random": random}
            try:
                exec(variables_code, {}, context)
            except Exception as e:
                raise serializers.ValidationError(
                    {"body": f"Error ejecutando las variables: {e}"}
                )

            # Extraer variables usadas en enunciado y respuestas

            def encontrar_variables(texto):
                """Encuentra todas las variables en un string con formato {variable}."""
                if not isinstance(
                    texto, str
                ):  # Si no es un string, retornamos un conjunto vacío
                    return set()
                return set(re.findall(r"\{(\w+)\}", texto))

            variables_usadas = set()
            variables_usadas.update(encontrar_variables(body["enunciado"]))
            for resp in body["respuestas"]:
                variables_usadas.update(encontrar_variables(resp[1]))

            if not variables_usadas.issubset(context.keys()):
                raise serializers.ValidationError(
                    {
                        "body": f"Hay variables en el enunciado o respuestas que no están definidas en 'variables'. Variables usadas: {variables_usadas}. Variables definidas: {set(context.keys())}"
                    }
                )

            # Validar respuestas como lista de tuplas (UUID, str, bool)
            if not isinstance(body["respuestas"], list):
                raise serializers.ValidationError(
                    {"body": "'respuestas' debe ser una lista."}
                )

            # Validar respuestas
            new_respuestas = []
            for resp in body["respuestas"]:
                if not isinstance(resp, list) or len(resp) not in [2, 3]:
                    raise serializers.ValidationError(
                        {
                            "body": "Cada respuesta debe ser una lista de 2 o 3 elementos."
                        }
                    )
                if len(resp) == 2:
                    resp_id = str(uuid.uuid4())
                    new_respuestas.append([resp_id, resp[0], resp[1]])
                else:
                    new_respuestas.append([resp[0], resp[1], resp[2]])

            body["respuestas"] = new_respuestas

        return data


def to_representation(self, instance):
    data = super().to_representation(instance)
    body = data.get("body", "{}")  # Asegura que sea un string JSON

    # Convertir body a diccionario si es un string
    if isinstance(body, str):
        try:
            body = json.loads(body)  # Convertir JSON string a diccionario
        except json.JSONDecodeError:
            raise serializers.ValidationError({"body": "Formato JSON inválido"})

    # Ejecutar código de variables
    variables_code = body.get("variables", "")
    context = {"random": random}

    try:
        exec(variables_code, {}, context)
    except Exception as e:
        raise serializers.ValidationError(
            {"body": f"Error ejecutando las variables: {e}"}
        )

    # Función para evaluar expresiones dentro de {}
    def evaluar_expresion(match):
        expr = match.group(1)
        try:
            return str(eval(expr, {}, context))  # Evaluar usando el contexto
        except Exception:
            return match.group(0)  # Dejar la expresión como está si falla

    # Aplicar evaluación en enunciado y respuestas
    pattern = re.compile(r"\{(.*?)\}")  # Captura contenido dentro de {}

    body["enunciado"] = pattern.sub(evaluar_expresion, body["enunciado"])
    body["respuestas"] = [
        [resp[0], pattern.sub(evaluar_expresion, resp[1]), resp[2]]
        for resp in body["respuestas"]
    ]

    data["body"] = body
    return data
