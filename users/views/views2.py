from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from ..models.models import UserProfile
from ..serializers.serializer import UserSerializer
from .utils import get_jwt_token

class EmailSignup(APIView):
    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string'},
                'password': {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'}
            }
        }},
        responses={
            201: {'type': 'object', 'properties': {
                'access_token': {'type': 'string'},
                'user': {'$ref': '#/components/schemas/User'}
            }},
            400: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        },
        description='Register new user with email and password',
        tags=['authentication']
    )
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')

            if not email or not password:
                raise ValidationError('Email and password are required')

            try:
                user = User.objects.get(email=email)
                if not hasattr(user, 'userprofile'):
                    # User exists from Google login, add password
                    user.set_password(password)
                    user.save()
                else:
                    raise ValidationError('User already exists')
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                UserProfile.objects.create(
                    user=user,
                    email=email,
                    given_name=first_name,
                    family_name=last_name,
                    role='student'
                )

            token = get_jwt_token(user)
            serializer = UserSerializer(user)
            return Response(
                {'access_token': token, 'user': serializer.data},
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Registration failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EmailLogin(APIView):
    @extend_schema(
        request={'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string'},
                'password': {'type': 'string'}
            }
        }},
        responses={
            200: {'type': 'object', 'properties': {
                'access_token': {'type': 'string'},
                'user': {'$ref': '#/components/schemas/User'}
            }},
            401: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        },
        description='Login with email and password',
        tags=['authentication']
    )
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                raise ValidationError('Email and password are required')

            user = authenticate(username=email, password=password)
            if not user:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            token = get_jwt_token(user)
            serializer = UserSerializer(user)
            return Response({'access_token': token, 'user': serializer.data})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Login failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )