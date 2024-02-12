from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserListSerializer
)
from .models import User
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django.core.mail import send_mail
from django.conf import settings

class AuthUserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()
            status_code = status.HTTP_201_CREATED

            user_email = serializer.data['email']
            send_mail(
                'Welcome to our website!',
                'Thank you for registering on our website!',
                settings.EMAIL_HOST_USER,
                [user_email],
                fail_silently=True,
            )

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'User Created Successfully',
                'user': serializer.data
            }
            return Response(response, status=status_code)

class AuthUserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK

        respose = {
            'success': True,
            'statusCode': status_code,
            'message': 'User Logged In Successfully',
            'access': serializer.data['access'],
            'refresh': serializer.data['refresh'],
            'authenticatd_user': {
                'email': serializer.data['email'],
                'role': serializer.data['role']
            }
        }

        return Response(respose, status=status_code)
    
class UserListView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.role != 1:
            response ={
                'success': False,
                'statusCode': status.HTTP_403_FORBIDDEN,
                'message': 'You are not authorized to view this page'
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        else:
            users = User.objects.all()
            serializer = self.serializer_class(users, many=True)
            response = {
                'success': True,
                'statusCode': status.HTTP_200_OK,
                'users': serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        
class ApiRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        return Response({
            'register': reverse('register', request=request, format=format),
            'login': reverse('login', request=request, format=format),
            'users': reverse('users', request=request, format=format),
            'token_create': reverse('token_create', request=request, format=format),
            'token_refresh': reverse('token_refresh', request=request, format=format)
        })