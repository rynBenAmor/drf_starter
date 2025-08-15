from django.middleware.csrf import get_token
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
from rest_framework_simplejwt.exceptions import InvalidToken



class UserInfoView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = RegisteredUserSerializer


class UserLoginView(APIView):
    def post(self, request):
        # ? validation
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            # ? refresh token creation
            refresh_token =  RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
    
            # ? send user info and tokens to client side
            response = Response({
                "user": UserSerializer(user).data,
            }, status=status.HTTP_200_OK
            )

            # ? httponly cookie jwt token
            response.set_cookie(key='refresh_token', value=str(refresh_token), httponly=True, samesite='None', secure=True)
            response.set_cookie(key='access_token', value=access_token, httponly=True, samesite='None', secure=True, max_age=300)

            # ? js readable csrf token for the frontend to send back as 'X-CSRFToken': getCookie('csrftoken'),
            csrf_token = get_token(request)
            response.set_cookie(key='csrftoken', value=csrf_token, httponly=False, secure=True, samesite='None')
            return response
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLogoutView(APIView):

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()
            except Exception as e :
                return Response({"error": f"error while logging out, {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            response = Response({"message": "You were successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            

        else:
            response = Response({"error": "no refresh token was found in the request object"}, status=status.HTTP_401_UNAUTHORIZED)

        return response
    



class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request):

        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "no refresh token was found in the request object"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({"message": "access token refreshed successfully, come back again :)"}, status=status.HTTP_200_OK)
            response.set_cookie(key='access_token', value=access_token, httponly=True, samesite='None', secure=True)
            return response
        
        except InvalidToken as e:
            return Response({"error": f"invalid token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED) 