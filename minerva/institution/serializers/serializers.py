from rest_framework import serializers
from ..models.models import Institution

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'name', 'description', 'url', 'image', 'icon']