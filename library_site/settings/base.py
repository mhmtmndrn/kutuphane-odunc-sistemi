"""Settings shared by every environment (dev, test, prod).

Configuration comes from environment variables (architecture §6.4, phase 3
small decision 16). ``dev`` and ``test`` provide defaults for the variables
read here before importing this module; ``prod`` requires all of them (KL-43).
"""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def env(name: str, default: str | None = None) -> str:
    """Return the environment variable ``name``.

    Raises ``ImproperlyConfigured`` when the variable is undefined and no
    ``default`` is given, so a missing setting stops the process at start-up.
    """
    value = os.environ.get(name)
    if value is not None:
        return value
    if default is not None:
        return default
    raise ImproperlyConfigured(f"Eksik ortam değişkeni: {name}")


SECRET_KEY = env("LIBRARY_SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
    "accounts",
]

AUTH_USER_MODEL = "accounts.StaffUser"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Last, as django-axes requires: turns a lockout into the 429 login page.
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "library_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "library_site.wsgi.application"

# SQLite in WAL mode with IMMEDIATE transactions (ADR-0002, data-design §5).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": env("LIBRARY_DB_PATH"),
        "OPTIONS": {
            "transaction_mode": "IMMEDIATE",
            "init_command": (
                "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; "
                "PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;"
            ),
        },
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Argon2 first (NFR-06); the others only verify hashes of older algorithms.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# Password rules (KL-9, phase 1 small decision 9): Django's four default
# validators, at least 10 characters.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Login and the 30-minute idle session (FR-27, architecture §6.1).
LOGIN_URL = "/giris/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/giris/"
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True

# Account lockout with django-axes (ADR-0009, ADR-0049, ADR-0050).
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_RESET_ON_SUCCESS = True
AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False
AXES_LOCKOUT_CALLABLE = "accounts.views.lockout_response"

SILENCED_SYSTEM_CHECKS = [
    # axes.W006 asks for "ip_address" in AXES_LOCKOUT_PARAMETERS. ADR-0009
    # locks by username only: behind Caddy every request comes from
    # 127.0.0.1, so an IP lock would lock out the whole staff at once.
    "axes.W006",
]

# Turkish only, Europe/Istanbul (NFR-09, phase 1 small decision 10).
LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Operations paths and scheduler switch (architecture §6.4; used by G14, G16).
LIBRARY_BACKUP_DIR = env("LIBRARY_BACKUP_DIR")
LIBRARY_EXPORT_DIR = env("LIBRARY_EXPORT_DIR")
LIBRARY_EXPORT_PASSPHRASE_FILE = env("LIBRARY_EXPORT_PASSPHRASE_FILE")
LIBRARY_SCHEDULER_ENABLED = env("LIBRARY_SCHEDULER_ENABLED", "0")
