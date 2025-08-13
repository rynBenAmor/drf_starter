# middleware.py
from django.middleware.csrf import get_token

class InjectCsrfCookieMiddleware:
    """
    a simple middleware that injects a csrf token to the response and delegates checking logic to the 'django.middleware.csrf.CsrfViewMiddleware'
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        get_token(request)
        if 'csrftoken' not in request.COOKIES:
            response.set_cookie(
                key='csrftoken',
                value=request.META.get("CSRF_COOKIE"),
                httponly=False,
                secure=True,
                samesite='None'
            )
        return response
