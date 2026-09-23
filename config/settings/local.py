from .base import *  # noqa: E402,F403


DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

MAILERS["default"]["BACKEND"] = "django.core.mail.backends.console.EmailBackend"
