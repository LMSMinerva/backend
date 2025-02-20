from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from content.models.content import Content
from content.serializers import ContentSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

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
            contents = Content.objects.filter(id_module_id=module_id)
        else:
            contents = Content.objects.all()

        serializer = ContentSerializer(contents, many=True)
        return Response(serializer.data)

    @extend_schema(request=ContentSerializer, responses=ContentSerializer)
    def post(self, request):
        """
        Create a new content object.
        """
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
        Retrieve a single content object by UUID.
        """
        content = get_object_or_404(Content, id=id)
        serializer = ContentSerializer(content)
        return Response(serializer.data)

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
