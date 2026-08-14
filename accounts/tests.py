from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="securePassword123",
            first_name="TestUser"
        )

    def test_registration_success(self):
        response = self.client.post(reverse("register"), {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_registration_password_mismatch(self):
        response = self.client.post(reverse("register"), {
            "name": "Mismatch User",
            "email": "mismatch@example.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword!"
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="mismatch@example.com").exists())

    def test_registration_duplicate_email(self):
        response = self.client.post(reverse("register"), {
            "name": "Duplicate User",
            "email": "test@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse("login"), {
            "email": "test@example.com",
            "password": "securePassword123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_case_insensitive(self):
        response = self.client.post(reverse("login"), {
            "email": "Test@EXAMPLE.com",
            "password": "securePassword123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_invalid_password(self):
        response = self.client.post(reverse("login"), {
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)

    def test_protected_routes_redirect_unauthenticated(self):
        protected_urls = [
            reverse("dashboard"),
            reverse("chat"),
            reverse("knowledge_bases"),
            reverse("upload"),
            reverse("profile_root"),
            reverse("analytics_root"),
            reverse("history_root"),
            reverse("settings_root"),
        ]
        for url in protected_urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 302, f"Expected redirect for unauthenticated access to {url}")
            self.assertTrue(res.url.startswith(reverse("login")))

    def test_authenticated_access_to_dashboard(self):
        self.client.login(username="test@example.com", password="securePassword123")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
