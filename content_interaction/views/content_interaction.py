from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from content_interaction.models.content_interaction import ContentInteraction
from content_interaction.serializers.content_interaction import (
    ContentInteractionSerializer,
)


class ContentInteractionListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    """
    API endpoints for CRUD operations on content interaction objects.
    """

    @extend_schema(
        request=None,
        responses=ContentInteractionSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name="content",
                type=OpenApiTypes.UUID,
                description="The UUID of the content to filter interactions by.",
                required=False,
            )
        ],
    )
    def get(self, request):
        """
        Retrieve all content interactions, or filter by content if content_id is provided.
        """
        content_id = request.query_params.get("content")

        if content_id:
            interactions = ContentInteraction.objects.filter(content_id=content_id)
        else:
            interactions = ContentInteraction.objects.all()

        serializer = ContentInteractionSerializer(interactions, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ContentInteractionSerializer, responses=ContentInteractionSerializer
    )
    def post(self, request):
        """
        Create a new content interaction.
        """
        serializer = ContentInteractionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentInteractionDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=ContentInteractionSerializer)
    def get(self, request, id):
        """
        Retrieve a single content interaction by UUID.
        """
        interaction = get_object_or_404(ContentInteraction, id=id)
        serializer = ContentInteractionSerializer(interaction)
        return Response(serializer.data)

    @extend_schema(
        request=ContentInteractionSerializer, responses=ContentInteractionSerializer
    )
    def put(self, request, id):
        """
        Update an existing content interaction by UUID.
        """
        interaction = get_object_or_404(ContentInteraction, id=id)
        serializer = ContentInteractionSerializer(
            interaction, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, id):
        """
        Delete a content interaction by UUID.
        """
        interaction = get_object_or_404(ContentInteraction, id=id)
        interaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
