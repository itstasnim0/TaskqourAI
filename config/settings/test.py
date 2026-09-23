from .base import *


DEBUG = False
AUTH_COOKIE_SECURE = False

SECRET_KEY = "test-only-secret-key"

ALLOWED_HOSTS = ["testserver", "localhost"]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
