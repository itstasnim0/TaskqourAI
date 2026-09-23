from .base import *  # noqa: E402,F403


DEBUG = True
AUTH_COOKIE_SECURE = False

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

MAILERS["default"]["BACKEND"] = "django.core.mail.backends.console.EmailBackend"
