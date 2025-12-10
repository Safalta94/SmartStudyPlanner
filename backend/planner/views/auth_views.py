from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

# --------------------------------------------------
# SIGNUP API (Public)
# --------------------------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can access
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')  # Optional
    password = request.data.get('password')

    # Validation
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    # Generate Auth Token
    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {'message': 'User created successfully', 'token': token.key},
        status=status.HTTP_201_CREATED
    )


# --------------------------------------------------
# LOGIN API (Public)
# --------------------------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Optional: Django login (for session-based auth if needed)
    django_login(request, user)

    # Generate or get existing token
    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {'message': 'Login successful', 'token': token.key},
        status=status.HTTP_200_OK
    )


# --------------------------------------------------
# LOGOUT API (Protected)
# --------------------------------------------------
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        # Delete the token to log out user
        request.user.auth_token.delete()

        # Optional: Django logout (if using sessions)
        django_logout(request)

        return Response(
            {'message': 'Logged out successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
