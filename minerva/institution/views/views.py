from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from ..models.models import Institution
from ..serializers.serializers import InstitutionSerializer
from drf_spectacular.utils import extend_schema


class InstitutionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=InstitutionSerializer(many=True))
    def get(self, request):
        """
        Retrieve all Institution objects.
        """
        institutions = Institution.objects.all()
        serializer = InstitutionSerializer(institutions, many=True)
        return Response(serializer.data)

    @extend_schema(request=InstitutionSerializer, responses=InstitutionSerializer)
    def post(self, request):
        """
        Create a new Institution object.
        """
        serializer = InstitutionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InstitutionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=InstitutionSerializer)
    def get(self, request, id):
        """
        Retrieve a single Institution object by UUID.
        """
        institution = get_object_or_404(Institution, id=id)
        serializer = InstitutionSerializer(institution)
        return Response(serializer.data)

    @extend_schema(request=InstitutionSerializer, responses=InstitutionSerializer)
    def put(self, request, id):
        """
        Update an existing Institution object by UUID.
        """
        institution = get_object_or_404(Institution, id=id)
        serializer = InstitutionSerializer(institution, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, id):
        """
        Delete an Institution object by UUID.
        """
        institution = get_object_or_404(Institution, id=id)
        institution.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
