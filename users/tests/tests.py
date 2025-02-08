from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from unittest.mock import patch
from ..views.utils import get_id_token_with_code

class GoogleAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login-with-google')
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com'
        )

    @patch('users.utils.get_id_token_with_code')
    def test_successful_login(self, mock_get_token):
        mock_get_token.return_value = {'email': 'test@example.com'}
        response = self.client.post(self.login_url, {'code': 'valid_code'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        self.assertIn('user', response.data)

    def test_login_without_code(self):
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, 400)

    @patch('users.utils.get_id_token_with_code')
    def test_login_creates_new_user(self, mock_get_token):
        mock_get_token.return_value = {'email': 'new@example.com'}
        response = self.client.post(self.login_url, {'code': 'valid_code'})
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_logout(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, 200)