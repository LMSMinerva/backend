from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from course_category.models import CourseCategory
from course_category.serializers import CourseCategorySerializer
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class CourseCategoryListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=CourseCategorySerializer(many=True))
    def get(self, request):
        """
        Retrieve all CourseCategory objects.
        """
        course_categories = CourseCategory.objects.all()
        serializer = CourseCategorySerializer(course_categories, many=True)
        return Response(serializer.data)

    @extend_schema(request=CourseCategorySerializer, responses=CourseCategorySerializer)
    def post(self, request):
        """
        Create a new CourseCategory object.
        """
        serializer = CourseCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseCategoryDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=None, responses=CourseCategorySerializer)
    def get(self, request, id):
        """
        Retrieve a single CourseCategory object by UUID.
        """
        course_category = get_object_or_404(CourseCategory, id=id)
        serializer = CourseCategorySerializer(course_category)
        return Response(serializer.data)

    @extend_schema(request=CourseCategorySerializer, responses=CourseCategorySerializer)
    def put(self, request, id):
        """
        Update an existing CourseCategory object by UUID.
        """
        course_category = get_object_or_404(CourseCategory, id=id)
        serializer = CourseCategorySerializer(course_category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, id):
        """
        Delete a CourseCategory object by UUID.
        """
        course_category = get_object_or_404(CourseCategory, id=id)
        course_category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
