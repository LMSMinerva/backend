from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from ..serializers.serializer import UserSerializer

from .utils import get_id_token_with_code

def authenticate_or_create_user(email):
    """
    Get existing user or create new one based on email.
    
    Args:
        email (str): User's email address
    
    Returns:
        User: Django User instance
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(username=email, email=email)
    return user

def get_jwt_token(user):
    """
    Generate JWT token for user.
    
    Args:
        user (User): Django User instance
    
    Returns:
        str: JWT access token
    """

    token = AccessToken.for_user(user)
    return str(token)

class LoginWithGoogle(APIView):
    """Handle Google OAuth login process."""

    def post(self,request):
        """
        Process Google OAuth code and return JWT token.
        
        Args:
            request: HTTP request containing Google OAuth code
            
        Returns:
            Response: JWT token and username if successful
        """
        if "code" not in request.data.keys():
            return Response(
                {"error": "Code is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        code = request.data['code']
        id_token = get_id_token_with_code(code)

        if not id_token:
            return Response(
                {"error": "Invalid code"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_email = id_token['email']
        user = authenticate_or_create_user(user_email)
        token = get_jwt_token(user)

        serializer = UserSerializer(user)
        return Response({'access_token': token, 'user': serializer.data})

class LogoutView(APIView):
    """Handle user logout."""
    
    def post(self, request):
        """
        Logout user and blacklist JWT token.
        
        Returns:
            Response: Success message
        """
        logout(request)
        return Response({"message": "Successfully logged out"})