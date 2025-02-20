from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from content_category.models import ContentCategory
from content_category.serializers import ContentCategorySerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class ContentCategoryListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=ContentCategorySerializer(many=True))
    def get(self, request):
        """
        Retrieve all contentCategory objects.
        """
        content_categories = ContentCategory.objects.all()
        serializer = ContentCategorySerializer(content_categories, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=ContentCategorySerializer, responses=ContentCategorySerializer
    )
    def post(self, request):
        """
        Create a new contentCategory object.
        """
        serializer = ContentCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentCategoryDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=ContentCategorySerializer)
    def get(self, request, id):
        """
        Retrieve a single contentCategory object by UUID.
        """
        content_category = get_object_or_404(ContentCategory, id=id)
        serializer = ContentCategorySerializer(content_category)
        return Response(serializer.data)

    @extend_schema(
        request=ContentCategorySerializer, responses=ContentCategorySerializer
    )
    def put(self, request, id):
        """
        Update an existing contentCategory object by UUID.
        """
        content_category = get_object_or_404(ContentCategory, id=id)
        serializer = ContentCategorySerializer(content_category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, id):
        """
        Delete a contentCategory object by UUID.
        """
        content_category = get_object_or_404(ContentCategory, id=id)
        content_category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
