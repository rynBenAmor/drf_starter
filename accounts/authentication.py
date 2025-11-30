# authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions



def enforce_csrf(request):
    """
    Enforce CSRF validation for cookie-based authentication.
    """
    check = CSRFCheck(request)
    # populates request.META['CSRF_COOKIE'], which is used in process_view()
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        # CSRF failed, reason is a rejection message
        raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')


class HybridJwtAuthentication(JWTAuthentication):
    """
    Authentication class that supports both Bearer tokens (Header) and HttpOnly Cookies.
    - If 'Authorization' header is present, it is used (No CSRF check).
    - If no header, 'access_token' cookie is used (CSRF check ENFORCED).
    """
    def authenticate(self, request):
        header = self.get_header(request) # returns HTTP_AUTHORIZATION request header
        
        if header is not None:
            # 1. Try Bearer Token (Header)
            raw_token = self.get_raw_token(header)
            if raw_token is not None:
                try:
                    validated_token = self.get_validated_token(raw_token)
                    return self.get_user(validated_token), validated_token
                except AuthenticationFailed:
                    # If header is present but invalid, fail immediately
                    raise AuthenticationFailed("Invalid token")
        
        # 2. Try Cookie
        access_token = request.COOKIES.get("access_token")
        if access_token:
            # Enforce CSRF for cookie-based auth
            enforce_csrf(request)
            
            try: 
                validated_token = self.get_validated_token(access_token)
                user = self.get_user(validated_token)
                return user, validated_token
            except AuthenticationFailed as e:
                raise AuthenticationFailed(f"access token validation failed: {str(e)}")

        return None # no authentication



class HttpOnlyCookieAuthentication(JWTAuthentication):
    """
    Authentication class that supports only HttpOnly Cookies.
    """
    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")

        if access_token:
            # Enforce CSRF for cookie-based auth
            enforce_csrf(request)
            
            try: 
                validated_token = self.get_validated_token(access_token)
                user = self.get_user(validated_token)
                return user, validated_token
            except AuthenticationFailed as e:
                raise AuthenticationFailed(f"access token validation failed: {str(e)}")

        return None # no authentication

