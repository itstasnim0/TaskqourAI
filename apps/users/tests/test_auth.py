from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_normalizes_email_and_hashes_password(self):
        user = User.objects.create_user(
            email="Person@EXAMPLE.com",
            password="Strong-pass-47!",
            full_name="Person Example",
        )

        self.assertEqual(user.email, "Person@example.com")
        self.assertTrue(user.check_password("Strong-pass-47!"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_sets_privileges(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="Strong-pass-48!",
            full_name="Admin User",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class AuthenticationAPITests(TestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.refresh_url = reverse("token_refresh")
        self.logout_url = reverse("logout")
        self.me_url = reverse("me")
        self.password = "Sufficiently-Strong-47!"

    def create_user(self, **overrides):
        data = {
            "email": "member@example.com",
            "password": self.password,
            "full_name": "Member Example",
        }
        data.update(overrides)
        return User.objects.create_user(**data)

    def login(self, **overrides):
        payload = {"email": "member@example.com", "password": self.password}
        payload.update(overrides)
        return self.client.post(self.login_url, payload, content_type="application/json")

    def test_registration_creates_user_profile_and_rejects_duplicate_email(self):
        payload = {
            "email": "member@example.com",
            "password": self.password,
            "full_name": "Member Example",
            "phone": "+15551234567",
            "locale": "en",
        }
        response = self.client.post(self.register_url, payload, content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], payload["email"])
        self.assertEqual(response.json()["full_name"], payload["full_name"])
        self.assertEqual(response.json()["phone"], payload["phone"])
        self.assertEqual(response.json()["locale"], payload["locale"])
        self.assertIn("created_at", response.json())
        self.assertNotIn("password", response.json())
        self.assertTrue(User.objects.get(email=payload["email"]).check_password(self.password))

        duplicate = self.client.post(self.register_url, payload, content_type="application/json")
        self.assertEqual(duplicate.status_code, 400)

    def test_registration_requires_valid_email_and_full_name(self):
        invalid_payloads = (
            {"email": "not-an-email", "password": self.password, "full_name": "Member"},
            {"email": "member@example.com", "password": self.password},
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    self.register_url,
                    payload,
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 400)

        self.assertFalse(User.objects.filter(email="member@example.com").exists())

    def test_login_sets_httponly_token_cookies_without_returning_tokens(self):
        self.create_user()

        response = self.login()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("access", response.json())
        self.assertNotIn("refresh", response.json())
        for name in ("access_token", "refresh_token"):
            self.assertIn(name, response.cookies)
            self.assertTrue(response.cookies[name]["httponly"])
            self.assertEqual(response.cookies[name]["samesite"], "Lax")
            self.assertFalse(response.cookies[name]["secure"])

    @override_settings(AUTH_COOKIE_SECURE=True)
    def test_login_marks_auth_cookies_secure_when_enabled(self):
        self.create_user()

        response = self.login()

        self.assertTrue(response.cookies["access_token"]["secure"])
        self.assertTrue(response.cookies["refresh_token"]["secure"])

    def test_login_rejects_invalid_credentials_and_inactive_users(self):
        self.create_user()

        wrong_password = self.login(password="wrong")
        self.assertEqual(wrong_password.status_code, 400)

        User.objects.filter(email="member@example.com").update(is_active=False)
        inactive_user = self.login()
        self.assertEqual(inactive_user.status_code, 400)

    def test_refresh_requires_refresh_cookie(self):
        response = self.client.post(self.refresh_url)

        self.assertEqual(response.status_code, 400)

    def test_refresh_issues_new_access_cookie(self):
        self.create_user()
        self.login()

        response = self.client.post(self.refresh_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"detail": "Tokens refreshed."})
        self.assertIn("access_token", response.cookies)
        self.assertNotIn("access", response.json())

    def test_me_requires_auth_cookie_and_returns_user_profile(self):
        anonymous_response = self.client.get(self.me_url)
        self.assertEqual(anonymous_response.status_code, 401)

        header_only_response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION="Bearer header-token-is-not-used",
        )
        self.assertEqual(header_only_response.status_code, 401)

        self.create_user()
        self.login()
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "member@example.com")
        self.assertEqual(response.json()["full_name"], "Member Example")
        self.assertIn("created_at", response.json())
        self.assertNotIn("password", response.json())

    def test_logout_clears_auth_cookies(self):
        self.create_user()
        self.login()

        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"detail": "Logged out successfully."})
        for name in ("access_token", "refresh_token"):
            self.assertEqual(response.cookies[name]["max-age"], 0)
