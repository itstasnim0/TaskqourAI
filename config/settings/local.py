from dotenv import load_dotenv

load_dotenv()

from .base import *  # noqa: E402,F403


DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
