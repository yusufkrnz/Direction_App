from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = '/api/v1/auth/register/'
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'bolum': 'sayisal'
        }

    def test_user_registration_success(self):
        """Kullanıcı başarıyla kayıt olabilir"""
        pass

    def test_user_registration_password_mismatch(self):
        """Şifreler eşleşmezse hata döner"""
        pass

    def test_user_registration_duplicate_email(self):
        """Aynı email ile tekrar kayıt olmaya izin verilmez"""
        pass


class UserLoginTests(APITestCase):
    def setUp(self):
        self.login_url = '/api/v1/auth/login/'
        
    def test_user_login_success(self):
        """Kullanıcı başarıyla giriş yapabilir"""
        pass

    def test_user_login_wrong_password(self):
        """Yanlış şifre ile giriş yapılamaz"""
        pass


class UserProfileTests(APITestCase):
    def setUp(self):
        self.profile_url = '/api/v1/auth/profile/'
        
    def test_get_profile_authenticated(self):
        """Kimlik doğrulanmış kullanıcı profilini görebilir"""
        pass

    def test_update_profile(self):
        """Kullanıcı profilini güncelleyebilir"""
        pass
