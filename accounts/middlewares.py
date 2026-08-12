# middleware.py
from django.middleware.csrf import get_token
from django.conf import settings

class InjectCsrfCookieMiddleware:
    """
    Middleware that ensures a CSRF token is set in request.META before view execution
    and attached to the response cookie using proper environment settings.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Ensure CSRF token is generated/retrieved BEFORE view processing
        csrf_token = get_token(request)

        response = self.get_response(request)

        # 2. Attach csrftoken cookie to response using settings configuration
        if csrf_token:
            response.set_cookie(
                key='csrftoken',
                value=csrf_token,
                httponly=False,  # Accessible to JS (Axios)
                secure=getattr(settings, 'CSRF_COOKIE_SECURE', False),
                samesite=getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax'),
                domain=getattr(settings, 'CSRF_COOKIE_DOMAIN', None),
                path=getattr(settings, 'CSRF_COOKIE_PATH', '/'),
            )
        return response

