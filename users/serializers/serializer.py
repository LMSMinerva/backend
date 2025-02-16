from rest_framework import serializers
from django.contrib.auth.models import User
from ..models.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['email', 'gender', 'birthday_date', 'role', 'picture', 'given_name', 'family_name', 'locale']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile']