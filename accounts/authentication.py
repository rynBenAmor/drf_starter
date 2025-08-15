# authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

class CookieJwtAuthentication(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None
        
        try: 
            validated_access_token = self.get_validated_token(access_token)
        
        except AuthenticationFailed as e:
            raise AuthenticationFailed(f"access token validation failed: {str(e)}")

        try:
            user = self.get_user(validated_access_token)
            return user, validated_access_token
        except AuthenticationFailed as e:
            raise AuthenticationFailed(f"error retrieving the user: {str(e)}")

