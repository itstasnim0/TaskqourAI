import pytest
from django.conf import settings
from apps.users.models import CustomUser


def test_auth_user_model_is_custom() -> None:
    assert settings.AUTH_USER_MODEL == "users.CustomUser"


@pytest.mark.django_db
def test_create_user_without_email_fails() -> None:
    with pytest.raises(ValueError, match="Email is required"):
        CustomUser.objects.create_user(email="", full_name="No Email")


@pytest.mark.django_db
def test_create_user_normalizes_email() -> None:
    user = CustomUser.objects.create_user(
        email="Member@EXAMPLE.COM",
        full_name="Member",
    )

    assert user.email == "Member@example.com"


@pytest.mark.django_db
def test_case_insensitive_email_lookup() -> None:
    created_user = CustomUser.objects.create_user(
        email="Test@X.com",
        full_name="Case Test",
    )

    found_user = CustomUser.objects.get(email="test@x.com")

    assert found_user == created_user


@pytest.mark.django_db
def test_create_superuser_flags() -> None:
    superuser = CustomUser.objects.create_superuser(
        email="admin@example.com",
        password="Admin-test-47!Strong",
        full_name="Admin",
    )

    assert superuser.is_staff is True
    assert superuser.is_superuser is True

    with pytest.raises(ValueError, match="is_staff=True"):
        CustomUser.objects.create_superuser(
            email="not-staff@example.com",
            password="Admin-test-47!Strong",
            full_name="Not Staff",
            is_staff=False,
        )

    with pytest.raises(ValueError, match="is_superuser=True"):
        CustomUser.objects.create_superuser(
            email="not-super@example.com",
            password="Admin-test-47!Strong",
            full_name="Not Super",
            is_superuser=False,
        )


@pytest.mark.django_db
def test_admin_add_user_page_renders(client) -> None:
    superuser = CustomUser.objects.create_superuser(
        email="admin@example.com",
        password="Admin-test-47!Strong",
        full_name="Admin",
    )
    client.force_login(superuser)

    response = client.get("/admin/users/user/add/")

    assert response.status_code == 200
