from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from course.models import Course
from course.serializers import CourseSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from module.serializers.module import ModuleSerializer


class CourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """
    API endpoints for CRUD operations on Course objects.
    """

    @extend_schema(
        request=None,
        responses=CourseSerializer(many=True),
    )
    def get(self, request):
        """
        Retrieve all Course objects.
        """
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    @extend_schema(request=CourseSerializer, responses=CourseSerializer)
    def post(self, request):
        """
        Create a new Course object.
        """
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseModulesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None,
        responses=ModuleSerializer(many=True),
    )
    def get(self, request, id):
        """
        Retrieve all modules of a course in order.
        """
        course = get_object_or_404(Course, id=id)
        modules = course.ordered_modules
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)


class CourseDetailViewById(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=CourseSerializer)
    def get(self, request, id):
        """
        Retrieve a single Course object by UUID.
        """
        course = get_object_or_404(Course, id=id)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    @extend_schema(request=CourseSerializer, responses=CourseSerializer)
    def put(self, request, id):
        """
        Update an existing Course object by UUID.
        """
        course = get_object_or_404(Course, id=id)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, id):
        """
        Delete a Course object by UUID.
        """
        course = get_object_or_404(Course, id=id)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CourseDetailViewBySlug(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=CourseSerializer)
    def get(self, request, alias):
        """
        Retrieve a single Course object by alias.
        """
        course = get_object_or_404(Course, alias=alias)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    @extend_schema(request=CourseSerializer, responses=CourseSerializer)
    def put(self, request, alias):
        """
        Update an existing Course object by alias.
        """
        course = get_object_or_404(Course, alias=alias)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, alias):
        """
        Delete a Course object by alias.
        """
        course = get_object_or_404(Course, alias=alias)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
