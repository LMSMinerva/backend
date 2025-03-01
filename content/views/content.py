import json
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from content.models.content import Content
from content.serializers import ContentSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import random


class ContentListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    """
    API endpoints for CRUD operations on content objects.
    """

    @extend_schema(
        request=None,
        responses=ContentSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name="module",
                type=OpenApiTypes.UUID,
                description="The UUID of the module to filter contents by.",
                required=False,
            )
        ],
    )
    def get(self, request):
        """
        Retrieve all content objects, or filter by module if module_id is provided.
        """
        module_id = request.query_params.get("module")
        if module_id:
            contents = Content.objects.filter(module_id=module_id)
        else:
            contents = Content.objects.all()
        serializer = ContentSerializer(contents, many=True)
        return Response(serializer.data)

    @extend_schema(request=ContentSerializer, responses=ContentSerializer)
    def post(self, request):
        """
        Create a new content object.
        """
        if request.data.get("content_type") == "seleccion":
            body = request.data.get("body")
            if isinstance(body, dict):
                # Convertir plantilla enunciado y respuestas a formato seguro
                body["enunciado"] = body["enunciado"].replace("${", "{")
                for i, respuesta in enumerate(body["respuestas"]):
                    body["respuestas"][i][1] = respuesta[1].replace("${", "{")

        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=ContentSerializer)
    def get(self, request, id):
        """
        Retrieve a single content object. If it's 'seleccion', process variables and responses dynamically.
        """
        content = get_object_or_404(Content, id=id)
        data = ContentSerializer(content).data
        if data["content_type"] == "seleccion":
            try:
                local_vars = {}
                exec(data["variables"], {}, local_vars)

                enunciado = data["enunciado"].format(**local_vars)
                respuestas = [
                    (r[0], r[1].format(**local_vars)) for r in data["respuestas"]
                ]

                return Response({"enunciado": enunciado, "respuestas": respuestas})
            except Exception as e:
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(data)

    @extend_schema(request=ContentSerializer, responses=ContentSerializer)
    def put(self, request, id):
        """
        Update an existing content object by UUID.
        """
        content = get_object_or_404(Content, id=id)
        serializer = ContentSerializer(content, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, id):
        """
        Delete a content object by UUID.
        """
        content = get_object_or_404(Content, id=id)
        content.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ValidateAnswerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """
        Validate if the selected answer IDs are correct.
        """
        content = get_object_or_404(Content, id=id)
        selected_ids = request.data.get("selected", [])  # Lista de IDs seleccionados
        body = (
            json.loads(content.body) if isinstance(content.body, str) else content.body
        )
        correct_ids = [r[0] for r in body["respuestas"] if r[2]]

        # Devolver lista con el estado de cada respuesta
        result = {"results": {rid: rid in correct_ids for rid in selected_ids}}
        return Response(result)
