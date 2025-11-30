# python manage.py test accounts.tests.test_authentication

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

class HybridAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.client = APIClient()
        self.user_info_url = reverse('user-info') # Assuming this is the name in urls.py

    def get_tokens(self):
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token), str(refresh)

    def test_bearer_authentication_success(self):
        """
        Test that Bearer token authentication works without CSRF token.
        """
        access_token, _ = self.get_tokens()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.user_info_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_cookie_authentication_requires_csrf(self):
        """
        Test that Cookie authentication FAILS without CSRF token.
        """
        access_token, _ = self.get_tokens()
        
        # We must enable CSRF checks in the client to ensure the request doesn't have 
        # the '_dont_enforce_csrf_checks' flag, which CSRFCheck respects.
        client = APIClient(enforce_csrf_checks=True)
        client.cookies['access_token'] = access_token
        
        # Ensure no header is sent
        client.credentials() 
        
        # This should fail because CSRF is enforced for cookies on unsafe methods
        response = client.patch(self.user_info_url, {'first_name': 'NewName'})
        # DRF's CSRFCheck usually returns 403 Permission Denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('CSRF Failed', str(response.data))

    def test_cookie_authentication_success_with_csrf(self):
        """
        Test that Cookie authentication SUCCEEDS with valid CSRF token.
        """
        access_token, _ = self.get_tokens()
        
        # 1. Get CSRF token first
        # We can use the login endpoint or just make a request to get the cookie
        # But APIClient handles CSRF automatically if 'enforce_csrf_checks' is True
        # Let's manually simulate the browser behavior
        
        client = APIClient(enforce_csrf_checks=True)
        client.cookies['access_token'] = access_token
        
        # We need to get a CSRF token first. 
        # Usually the frontend gets it from a cookie.
        # Let's make a safe request to populate the CSRF cookie
        client.get(reverse('user-login')) # Just to get the cookie
        
        # Now extract the csrf token from the cookie jar
        csrftoken = client.cookies['csrftoken'].value
        
        # Send the request with the cookie AND the header
        response = client.get(
            self.user_info_url,
            HTTP_X_CSRFTOKEN=csrftoken
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_hybrid_priority(self):
        """
        Test that Authorization header takes precedence over Cookie.
        """
        # Create another user
        other_user = User.objects.create_user(email='other@example.com', password='password123')
        other_refresh = RefreshToken.for_user(other_user)
        other_access = str(other_refresh.access_token)
        
        access_token, _ = self.get_tokens()
        
        # Set cookie for 'self.user'
        self.client.cookies['access_token'] = access_token
        
        # Set header for 'other_user'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_access}')
        
        response = self.client.get(self.user_info_url)
        
        # Should return other_user's info
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], other_user.email)

    def test_login_returns_tokens_in_body(self):
        """
        Test that login endpoint returns tokens in the body.
        """
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        response = self.client.post(reverse('user-login'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('access_token', response.cookies) # Should still set cookies
