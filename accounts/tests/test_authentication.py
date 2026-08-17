# python manage.py test accounts.tests.test_authentication

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class HttpOnlyAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testusername',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.client = APIClient()
        self.user_info_url = reverse('user-info')
        self.login_url = reverse('user-login')
        self.logout_url = reverse('user-logout')
        self.refresh_url = reverse('token-refresh')

    def get_tokens(self):
        refresh = RefreshToken.for_user(self.user)
        return str(refresh.access_token), str(refresh)

    def test_login_sets_httponly_and_csrf_cookies(self):
        """
        Test that login endpoint sets access_token, refresh_token and csrftoken cookies.
        """
        data = {
            'username': 'testusername',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        self.assertTrue(response.cookies['access_token']['httponly'])
        self.assertTrue(response.cookies['refresh_token']['httponly'])
        self.assertIn('csrftoken', response.cookies)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testusername')

    def test_repeat_logins_succeed_with_existing_access_token_cookie(self):
        """
        Verify that a second login request succeeds even when access_token cookie is present in browser.
        """
        data = {
            'username': 'testusername',
            'password': 'password123'
        }
        # First login
        res1 = self.client.post(self.login_url, data)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', res1.cookies)

        # Second login with access_token cookie present
        res2 = self.client.post(self.login_url, data)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', res2.cookies)

    def test_silent_reauthentication_with_cookie(self):
        """
        Test that GET /me/ returns user when valid access_token cookie is present.
        """
        access_token, _ = self.get_tokens()
        self.client.cookies['access_token'] = access_token

        response = self.client.get(self.user_info_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_silent_reauthentication_without_cookie_fails_401(self):
        """
        Test that GET /me/ returns 401 when no access_token cookie is present.
        """
        response = self.client.get(self.user_info_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_with_refresh_cookie(self):
        """
        Test that POST /token/refresh/ with refresh_token cookie issues a new access_token cookie.
        """
        _, refresh_token = self.get_tokens()
        self.client.cookies['refresh_token'] = refresh_token

        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        self.assertTrue(response.cookies['access_token']['httponly'])

    def test_token_refresh_without_cookie_fails_401(self):
        """
        Test that POST /token/refresh/ without refresh_token cookie returns 401.
        """
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_clears_cookies(self):
        """
        Test that POST /logout/ clears access_token and refresh_token cookies.
        """
        access_token, refresh_token = self.get_tokens()
        self.client.cookies['access_token'] = access_token
        self.client.cookies['refresh_token'] = refresh_token

        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify cookies are expired / deleted
        self.assertEqual(response.cookies['access_token'].value, '')
        self.assertEqual(response.cookies['refresh_token'].value, '')

    def test_cookie_authentication_requires_csrf_on_unsafe_methods(self):
        """
        Test that Cookie authentication FAILS without CSRF token on unsafe HTTP methods (PATCH/POST).
        """
        access_token, _ = self.get_tokens()
        client = APIClient(enforce_csrf_checks=True)
        client.cookies['access_token'] = access_token

        response = client.patch(self.user_info_url, {'email': 'newemail@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cookie_authentication_succeeds_with_csrf_header(self):
        """
        Test that Cookie authentication SUCCEEDS with valid CSRF token header.
        """
        access_token, _ = self.get_tokens()
        client = APIClient(enforce_csrf_checks=True)
        client.cookies['access_token'] = access_token

        # Initial GET request to get csrftoken cookie
        init_res = client.get(self.login_url)
        self.assertIn('csrftoken', init_res.cookies)
        csrftoken = init_res.cookies['csrftoken'].value
        client.cookies['csrftoken'] = csrftoken

        # Make PATCH request with CSRF header
        response = client.patch(
            self.user_info_url,
            {'email': 'newemail@example.com'},
            format='json',
            HTTP_X_CSRFTOKEN=csrftoken
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newemail@example.com')


class BearerAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testbearer',
            email='bearer@example.com',
            password='password123',
            first_name='Bearer',
            last_name='User'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123',
            first_name='Other',
            last_name='User'
        )
        self.client = APIClient()
        self.user_info_url = reverse('user-info')
        self.login_url = reverse('user-login')
        self.logout_url = reverse('user-logout')
        self.refresh_url = reverse('token-refresh')

    def get_tokens(self, user=None):
        target = user or self.user
        refresh = RefreshToken.for_user(target)
        return str(refresh.access_token), str(refresh)

    def test_login_returns_token_response(self):
        """
        Test that login returns user metadata as well as access and refresh tokens.
        """
        data = {
            'username': 'testbearer',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testbearer')

    def test_valid_bearer_token_authenticates_successfully(self):
        """
        Test that GET /me/ with Authorization: Bearer <token> returns authenticated user.
        """
        access_token, _ = self.get_tokens()
        response = self.client.get(
            self.user_info_url,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_invalid_bearer_token_is_rejected(self):
        """
        Test that GET /me/ with invalid Authorization header fails with 401.
        """
        response = self.client.get(
            self.user_info_url,
            HTTP_AUTHORIZATION='Bearer invalid_jwt_token'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_authentication_is_rejected_by_protected_endpoints(self):
        """
        Test that GET /me/ without any authentication returns 401.
        """
        response = self.client.get(self.user_info_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bearer_token_does_not_require_csrf_on_unsafe_methods(self):
        """
        Test that Bearer token auth bypasses CSRF requirement on PATCH/POST methods.
        """
        access_token, _ = self.get_tokens()
        client = APIClient(enforce_csrf_checks=True)

        response = client.patch(
            self.user_info_url,
            {'email': 'updated_bearer@example.com'},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'updated_bearer@example.com')

    def test_refresh_token_produces_new_access_token_via_body(self):
        """
        Test that POST /token/refresh/ with refresh token in body produces a new access token.
        """
        _, refresh_token = self.get_tokens()
        response = self.client.post(
            self.refresh_url,
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        new_access = response.data['access']

        # Verify new access token works for authentication
        me_res = self.client.get(
            self.user_info_url,
            HTTP_AUTHORIZATION=f'Bearer {new_access}'
        )
        self.assertEqual(me_res.status_code, status.HTTP_200_OK)
        self.assertEqual(me_res.data['username'], self.user.username)

    def test_invalid_or_expired_refresh_token_is_rejected(self):
        """
        Test that POST /token/refresh/ with invalid refresh token fails with 401.
        """
        response = self.client.post(
            self.refresh_url,
            {'refresh': 'invalid_refresh_token'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bearer_authentication_takes_precedence_over_cookie(self):
        """
        Test that when both Authorization: Bearer and cookie exist, Bearer is used.
        """
        bearer_access, _ = self.get_tokens(self.user)
        cookie_access, _ = self.get_tokens(self.other_user)

        self.client.cookies['access_token'] = cookie_access

        response = self.client.get(
            self.user_info_url,
            HTTP_AUTHORIZATION=f'Bearer {bearer_access}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertNotEqual(response.data['username'], self.other_user.username)

    def test_logout_with_refresh_token_body(self):
        """
        Test that POST /logout/ with refresh token in body succeeds.
        """
        _, refresh_token = self.get_tokens()
        response = self.client.post(
            self.logout_url,
            {'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

