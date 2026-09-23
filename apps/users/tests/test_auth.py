from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse


User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_normalizes_email_and_hashes_password(self):
        user = User.objects.create_user("Person@EXAMPLE.com", "Strong-pass-47!")
        self.assertEqual(user.email, "Person@example.com")
        self.assertTrue(user.check_password("Strong-pass-47!"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_sets_privileges(self):
        user = User.objects.create_superuser("admin@example.com", "Strong-pass-48!")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class AuthenticationAPITests(TestCase):
    def setUp(self):
        self.register_url = "/api/v1/auth/register/"
        self.login_url = "/api/v1/auth/login/"
        self.refresh_url = "/api/v1/auth/refresh/"
        self.me_url = "/api/v1/auth/me/"
        self.password = "Sufficiently-Strong-47!"

    def test_registration_creates_user_and_rejects_duplicate_email(self):
        payload = {"email": "member@example.com", "password": self.password}
        response = self.client.post(self.register_url, payload, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], payload["email"])
        self.assertIn("date_joined", response.json())
        self.assertNotIn("password", response.json())

        duplicate = self.client.post(self.register_url, payload, content_type="application/json")
        self.assertEqual(duplicate.status_code, 400)

    def test_registration_applies_django_password_validation(self):
        response = self.client.post(
            self.register_url,
            {"email": "member@example.com", "password": "password"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email="member@example.com").exists())

    def test_login_sets_httponly_token_cookies_without_returning_tokens_in_body(self):
        User.objects.create_user("member@example.com", self.password)
        response = self.client.post(
            self.login_url,
            {"email": "member@example.com", "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("access", response.json())
        self.assertNotIn("refresh", response.json())
        self.assertIn("access_token", self.client.cookies)
        self.assertIn("refresh_token", self.client.cookies)
        self.assertTrue(response.cookies["access_token"]["httponly"])
        self.assertTrue(response.cookies["refresh_token"]["httponly"])
        self.assertEqual(response.cookies["access_token"]["samesite"], "Lax")
        self.assertEqual(response.cookies["refresh_token"]["samesite"], "Lax")
        self.assertFalse(response.cookies["access_token"]["secure"])

    @override_settings(AUTH_COOKIE_SECURE=True)
    def test_login_marks_auth_cookies_secure_when_enabled(self):
        User.objects.create_user("member@example.com", self.password)
        response = self.client.post(
            self.login_url,
            {"email": "member@example.com", "password": self.password},
            content_type="application/json",
        )
        self.assertTrue(response.cookies["access_token"]["secure"])
        self.assertTrue(response.cookies["refresh_token"]["secure"])

    def test_login_rejects_invalid_credentials(self):
        User.objects.create_user("member@example.com", self.password)
        response = self.client.post(
            self.login_url,
            {"email": "member@example.com", "password": "wrong"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_refresh_returns_new_access_token(self):
        User.objects.create_user("member@example.com", self.password)
        self.client.post(
            self.login_url,
            {"email": "member@example.com", "password": self.password},
            content_type="application/json",
        )
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", self.client.cookies)
        self.assertNotIn("access", response.json())

    def test_me_requires_auth_cookie_and_returns_user_profile(self):
        anonymous_response = self.client.get(self.me_url)
        self.assertEqual(anonymous_response.status_code, 401)
        header_only_response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION="Bearer header-token-is-not-used",
        )
        self.assertEqual(header_only_response.status_code, 401)

        User.objects.create_user("member@example.com", self.password)
        self.client.post(
            self.login_url,
            {"email": "member@example.com", "password": self.password},
            content_type="application/json",
        )
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "member@example.com")
        self.assertIn("date_joined", response.json())
