"""Production settings. Every variable of architecture §6.4 is required (KL-43)."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import env

DEBUG = False

# No django.contrib.admin in production (ADR-0024).

ALLOWED_HOSTS = [
    host.strip() for host in env("LIBRARY_ALLOWED_HOSTS").split(",") if host.strip()
]


def _trusted_origin(host: str) -> str:
    # A leading dot is Django's subdomain wildcard; CSRF needs the "*." form.
    return f"https://*{host}" if host.startswith(".") else f"https://{host}"


CSRF_TRUSTED_ORIGINS = [_trusted_origin(host) for host in ALLOWED_HOSTS]

# Caddy serves /static/ from this directory (ADR-0029).
STATIC_ROOT = env("LIBRARY_STATIC_ROOT")

# Institutional SMTP account, port 587 with STARTTLS (ADR-0004).
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("LIBRARY_EMAIL_HOST")
_email_port = env("LIBRARY_EMAIL_PORT")
try:
    EMAIL_PORT = int(_email_port)
except ValueError as exc:
    raise ImproperlyConfigured(
        f"Geçersiz ortam değişkeni: LIBRARY_EMAIL_PORT={_email_port!r}"
    ) from exc
EMAIL_HOST_USER = env("LIBRARY_EMAIL_USER")
EMAIL_HOST_PASSWORD = env("LIBRARY_EMAIL_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env("LIBRARY_EMAIL_FROM")

# TLS is terminated by Caddy, which forwards the original scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SILENCED_SYSTEM_CHECKS = [
    # W004 (HSTS) and W008 (SSL redirect): Caddy redirects HTTP to HTTPS and
    # owns the TLS policy (ADR-0005), so Django does not set them itself.
    "security.W004",
    "security.W008",
]
