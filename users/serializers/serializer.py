from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with required fields for authentication."""
    class Meta:
        model = User
        fields = ('id', 'username', 'email')