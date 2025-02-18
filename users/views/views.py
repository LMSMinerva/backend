from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import logout
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenVerifyView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework.exceptions import ValidationError, ParseError
from ..models.models import UserProfile

import json
from ..serializers.serializer import UserSerializer

from .utils import get_id_token_with_code

def authenticate_or_create_user(id_token_data):
    """
    Get existing user or create new one based on email.
    
    Args:
        email (str): User's email address
    
    Returns:
        User: Django User instance
    """
    email = id_token_data['email']
    google_id = id_token_data['sub']

    if not google_id:
        raise ValidationError("Missing Google user ID")

    try:
        user = User.objects.get(email=email)
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'google_id': google_id,
                'picture': id_token_data.get('picture', ''),
                'given_name': id_token_data.get('given_name', ''),
                'family_name': id_token_data.get('family_name', ''),
                'locale': id_token_data.get('locale', ''),
                'email': email,
                'gender': id_token_data.get('gender', ''),
                'birthday_date': id_token_data.get('birthday', None),
                'role': 'student'
            }
        )
        if not created:
            # Update existing profile with latest data
            profile.picture = id_token_data.get('picture', profile.picture)
            profile.given_name = id_token_data.get('given_name', profile.given_name)
            profile.family_name = id_token_data.get('family_name', profile.family_name)
            profile.locale = id_token_data.get('locale', profile.locale)
            profile.save()
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=id_token_data.get('given_name', ''),
            last_name=id_token_data.get('family_name', '')
        )
        UserProfile.objects.create(
            user=user,
            google_id=google_id,
            picture=id_token_data.get('picture', ''),
            given_name=id_token_data.get('given_name', ''),
            family_name=id_token_data.get('family_name', ''),
            locale=id_token_data.get('locale', ''),
            email=email,
            gender=id_token_data.get('gender', ''),
            birthday_date=id_token_data.get('birthday', None),
            role='student'
        )

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
    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'code': {'type': 'string'}}}},
        responses={
            200: {'type': 'object', 'properties': {
                'access_token': {'type': 'string'},
                'user': {'$ref': '#/components/schemas/User'}
            }},
            400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        },
        description='Exchange Google OAuth code for JWT token and user profile data',
        tags=['authentication']
    )
    def post(self,request):
        """
        Process Google OAuth code and return JWT token.
        
        Args:
            request: HTTP request containing Google OAuth code
            
        Returns:
            Response: JWT token and username if successful
        """
        try:
            # Debug incoming request
            print("Request Content-Type:", request.content_type)
            print("Request body:", request.body.decode('utf-8'))
            
            if "code" not in request.data.keys():
                return Response(
                    {"error": "Code is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            code = request.data['code']
            id_token = get_id_token_with_code(code)

            if id_token == "Token verification error" or id_token =="Token verification error":
                return Response(
                    {"error": id_token}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = authenticate_or_create_user(id_token)
            token = get_jwt_token(user)

            serializer = UserSerializer(user)
            return Response({'access_token': token, 'user': serializer.data})
        except json.JSONDecodeError as e:
            return Response(
                {"error": f"Invalid JSON format: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "Authentication failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class LogoutView(GenericAPIView):
    @extend_schema(
        responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}},
        description='Logout user and invalidate JWT token',
        tags=['authentication']
    )
    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out"})
    
@extend_schema(
    request={'application/json': {'type': 'object', 'properties': {'token': {'type': 'string'}}}},
    responses={
        200: {'type': 'object', 'properties': {}},
        401: {'type': 'object', 'properties': {'detail': {'type': 'string'}}}
    },
    description='Verify JWT token validity',
    tags=['authentication']
)
class DocumentedTokenVerifyView(TokenVerifyView):
    pass