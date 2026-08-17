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
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings




class UserInfoView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):  # type: ignore[return-value]
        return self.request.user
    


class UserRegistrationView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegisteredUserSerializer




class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        # ? validation
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            # ? refresh token creation
            refresh_token =  RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
    
            # * send user info :
            data = {
                "user": UserSerializer(user).data
            }
            # * and tokens: important for generic JWTAuthentication/HybridJwtAuthentication classes
            if settings.AUTH_EXPOSE_TOKENS:
                data.update({
                    "access": access_token,
                    "refresh": str(refresh_token),
                })

            response = Response(data, status=status.HTTP_200_OK)

            # * set the httponly cookie jwt tokens: important for httpOnly authentication
            if settings.AUTH_USE_HTTPONLY_COOKIES:
                response.set_cookie(key='refresh_token', value=str(refresh_token), **settings.AUTH_COOKIE_SETTINGS)
                response.set_cookie(key='access_token', value=access_token, max_age=300, **settings.AUTH_COOKIE_SETTINGS)
                # ? InjectCsrfCookieMiddleware already injects the csrf token in every response if AUTH_USE_HTTPONLY_COOKIES is True
            
            
            return response
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
 