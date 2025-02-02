from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from course.models.course import Course
from module.models import Module
from module.serializers import ModuleSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class ModuleListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """
    API endpoints for CRUD operations on Module objects.
    """

    @extend_schema(
        request=None,
        responses=ModuleSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name="course_id",
                type=OpenApiTypes.UUID,
                description="The UUID of the course to filter modules by.",
                required=False,
            )
        ],
    )
    def get(self, request):
        """
        Retrieve all Module objects, or filter by course if course_id is provided.
        """
        course_id = request.query_params.get("course_id")

        if course_id:
            modules = Module.objects.filter(id_course_id=course_id)
        else:
            modules = Module.objects.all()

        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)

    @extend_schema(request=ModuleSerializer, responses=ModuleSerializer)
    def post(self, request):
        """
        Create a new Module object.
        """
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModuleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=ModuleSerializer)
    def get(self, request, id):
        """
        Retrieve a single Module object by UUID.
        """
        module = get_object_or_404(Module, id=id)
        serializer = ModuleSerializer(module)
        return Response(serializer.data)

    @extend_schema(request=ModuleSerializer, responses=ModuleSerializer)
    def put(self, request, id):
        """
        Update an existing Module object by UUID.
        """
        module = get_object_or_404(Module, id=id)
        serializer = ModuleSerializer(module, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, id):
        """
        Delete a Module object by UUID.
        """
        module = get_object_or_404(Module, id=id)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
