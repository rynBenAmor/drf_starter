from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import (
    UserSerializer,
    RegisteredUserSerializer,
    UserLoginSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)




class UserInfoView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    


class UserRegistrationView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegisteredUserSerializer




class UserLoginView(APIView):
    """
    Custom login view that:
    1. Validates credentials using DRF's standard serializer
    2. Sets HTTP-only cookies for JWT tokens (if configured)
    3. Returns user data + tokens in response (if configured)
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # 1. Use DRF's standard serializer for validation
        serializer = TokenObtainPairSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # Catch validation errors (invalid credentials, inactive user, etc.)
            logger.warning(f"Login failed: {str(e)}")
            return Response(
                {"detail": "Invalid credentials or inactive account."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. Get validated data (user and tokens)
        user = serializer.user
        access_token = serializer.validated_data["access"]
        refresh_token = serializer.validated_data["refresh"]

        # 3. Build response data
        response_data = {
            "user": UserSerializer(user).data,
            "message": "Login successful",
        }

        # 4. Optionally expose tokens in response body
        if settings.AUTH_EXPOSE_TOKENS:
            response_data.update({
                "access": access_token,
                "refresh": refresh_token,
            })

        response = Response(response_data, status=status.HTTP_200_OK)

        # 5. Set HTTP-only cookies if configured
        if settings.AUTH_USE_HTTPONLY_COOKIES:
            response.set_cookie(
                key='access_token',
                value=access_token,
                max_age=settings.AUTH_ACCESS_TOKEN_MAX_AGE or 300,
                **settings.AUTH_COOKIE_SETTINGS
            )
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                max_age=settings.AUTH_REFRESH_TOKEN_MAX_AGE or 86400 * 7,
                **settings.AUTH_COOKIE_SETTINGS
            )

        return response
    

class UserLogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh") or request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()
            except Exception:
                pass

        response = Response({"message": "You were successfully logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
    


class CookieTokenRefreshView(TokenRefreshView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh") or request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "no refresh token was found in the request object"}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError) as e:
            return Response({"error": f"invalid token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

        data = {
            "message": "access token refreshed successfully",
            "access": serializer.validated_data["access"],
        }
        if "refresh" in serializer.validated_data:
            data["refresh"] = serializer.validated_data["refresh"]

        response = Response(data, status=status.HTTP_200_OK)
        if settings.AUTH_USE_HTTPONLY_COOKIES:
            response.set_cookie(key='access_token', value=data["access"], max_age=300, **settings.AUTH_COOKIE_SETTINGS)
            if "refresh" in data:
                response.set_cookie(key='refresh_token', value=data["refresh"], **settings.AUTH_COOKIE_SETTINGS)
        else:
            response.set_cookie(key='access_token', value=data["access"])
        return response
 