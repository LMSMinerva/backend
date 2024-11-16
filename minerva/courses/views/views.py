from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from ..models.models import Course
from ..serializers.serializers import CourseSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
class CourseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """
    API endpoints for CRUD operations on Course objects.
    """
    @extend_schema(
        request=CourseSerializer,
        responses=CourseSerializer,
        parameters=[
            OpenApiParameter(name='name', type=OpenApiTypes.STR, description='Course name'),
            OpenApiParameter(name='alias', type=OpenApiTypes.STR, description='Course alias'),
            OpenApiParameter(name='category', type=OpenApiTypes.STR, description='Course category'),
            OpenApiParameter(name='visibility', type=OpenApiTypes.BOOL, description='Course visibility'),
            OpenApiParameter(name='description', type=OpenApiTypes.STR, description='Course description'),
            OpenApiParameter(name='format', type=OpenApiTypes.STR, description='Course format'),
            OpenApiParameter(name='creation_date', type=OpenApiTypes.DATE, description='Course creation date'),
            OpenApiParameter(name='id_instructor', type=OpenApiTypes.STR, description='ID of the instructor'),
            OpenApiParameter(name='total_students_enrolled', type=OpenApiTypes.INT, description='Total students enrolled'),
        ]
    )

    def get(self, request, pk=None):
        """
        Handle GET requests to retrieve a single course or all courses.
        """
        if pk:
            return self.get_course(pk)
        else:
            return self.get_courses()

    def get_course(self, pk):
        """
        Retrieve a single Course object by primary key.
        """
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    def get_courses(self):
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
    
    @extend_schema(request=CourseSerializer, responses=CourseSerializer)
    def put(self, request, pk):
        """
        Update an existing Course object.
        """
        course = get_object_or_404(Course, pk=pk)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(request=None, responses=None)
    def delete(self, request, pk):
        """
        Delete a Course object.
        """
        course = get_object_or_404(Course, pk=pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)