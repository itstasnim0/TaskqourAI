from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from .models import User


class UserAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(email="admin@example.com", password="Admin-test-47!Strong")
        cls.user = User.objects.create_user(email="member@example.com", full_name="Member")

    def setUp(self):
        self.client.force_login(self.superuser)

    def test_configuration_matches_custom_user(self):
        user_admin = admin.site._registry[User]
        model_fields = {field.name for field in User._meta.get_fields()}
        change_fields = flatten_fieldsets(user_admin.fieldsets)
        add_fields = flatten_fieldsets(user_admin.add_fieldsets)
        self.assertNotIn("username", change_fields + add_fields)
        self.assertTrue(set(change_fields) <= model_fields)
        self.assertTrue(set(add_fields) - {"password1", "password2"} <= model_fields)
        self.assertNotIn("password1", change_fields)
        self.assertNotIn("password2", change_fields)
        for fields in (user_admin.list_display, user_admin.search_fields, user_admin.ordering):
            self.assertTrue(set(fields) <= model_fields)
        self.assertTrue({"is_staff", "is_active", "is_superuser", "groups", "user_permissions"} <= set(change_fields))
        self.assertEqual(user_admin.add_form._meta.model, User)
        self.assertEqual(user_admin.form._meta.model, User)

    def test_changelist_and_search(self):
        url = reverse("admin:users_user_changelist")
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.get(url, {"q": "member@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)

    def test_add_page(self):
        response = self.client.get(reverse("admin:users_user_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')
        self.assertNotContains(response, 'name="username"')

    def test_change_page(self):
        response = self.client.get(reverse("admin:users_user_change", args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)

    def test_add_hashes_password(self):
        password = "New-user-48!Strong"
        response = self.client.post(reverse("admin:users_user_add"), {
            "email": "new@example.com", "password1": password, "password2": password,
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_add_rejects_mismatched_passwords(self):
        response = self.client.post(reverse("admin:users_user_add"), {
            "email": "invalid@example.com", "password1": "New-user-48!Strong", "password2": "different",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("password2", response.context["adminform"].form.errors)
        self.assertFalse(User.objects.filter(email="invalid@example.com").exists())

    def test_change_saves_permissions_and_preserves_password(self):
        group = Group.objects.create(name="Editors")
        permission = Permission.objects.get(content_type__app_label="catalog", codename="view_task")
        original_password = self.user.password
        response = self.client.post(reverse("admin:users_user_change", args=[self.user.pk]), {
            "email": self.user.email, "full_name": "Updated member", "phone": "", "locale": "en",
            "is_active": "on", "is_staff": "on", "is_superuser": "on",
            "groups": [str(group.pk)], "user_permissions": [str(permission.pk)],
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Updated member")
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)
        self.assertEqual(self.user.password, original_password)
        self.assertIn(group, self.user.groups.all())
        self.assertIn(permission, self.user.user_permissions.all())
