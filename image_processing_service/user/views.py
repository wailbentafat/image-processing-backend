from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if User.objects.filter(username=username).exists():
        return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(username=username, password=password)
    token = RefreshToken.for_user(user)
    return Response({'username': user.username, 'access': str(token.access_token), 'refresh': str(token)}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    token = RefreshToken.for_user(user)
    return Response({'username': user.username, 'access': str(token.access_token), 'refresh': str(token)}, status=status.HTTP_200_OK)
