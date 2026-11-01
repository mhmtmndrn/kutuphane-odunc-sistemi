"""Settings tests: production settings, time zone and password hashing (G01).

Production settings are loaded in a separate process so that their required
environment variables never leak into the test process (test plan §5).
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import date, datetime, timezone as dt_timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone

REPO_ROOT = Path(__file__).resolve().parent.parent

# KL-43: every variable of architecture §6.4 except DJANGO_SETTINGS_MODULE
# (read by Django) and LIBRARY_SCHEDULER_ENABLED (defaults to "0").
REQUIRED_PROD_VARS = (
    "LIBRARY_SECRET_KEY",
    "LIBRARY_DB_PATH",
    "LIBRARY_ALLOWED_HOSTS",
    "LIBRARY_BACKUP_DIR",
    "LIBRARY_EXPORT_DIR",
    "LIBRARY_EXPORT_PASSPHRASE_FILE",
    "LIBRARY_EMAIL_HOST",
    "LIBRARY_EMAIL_PORT",
    "LIBRARY_EMAIL_USER",
    "LIBRARY_EMAIL_PASSWORD",
    "LIBRARY_EMAIL_FROM",
    "LIBRARY_STATIC_ROOT",
)


def _prod_env(tmp_path: Path, *, drop: tuple[str, ...] = ()) -> dict[str, str]:
    """Build a clean environment with dummy production values."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("LIBRARY_") and key != "DJANGO_SETTINGS_MODULE"
    }
    env.update(
        {
            "DJANGO_SETTINGS_MODULE": "library_site.settings.prod",
            "PYTHONIOENCODING": "utf-8",
            "LIBRARY_SECRET_KEY": "test-only-" + "k7Qz9xR2mVb4Lp8sWn3Hd6Jf" * 3,
            "LIBRARY_DB_PATH": str(tmp_path / "library.sqlite3"),
            "LIBRARY_ALLOWED_HOSTS": "library.local",
            "LIBRARY_BACKUP_DIR": str(tmp_path / "backups"),
            "LIBRARY_EXPORT_DIR": str(tmp_path / "exports"),
            "LIBRARY_EXPORT_PASSPHRASE_FILE": str(tmp_path / "passphrase.txt"),
            "LIBRARY_EMAIL_HOST": "smtp.example.invalid",
            "LIBRARY_EMAIL_PORT": "587",
            "LIBRARY_EMAIL_USER": "library@example.invalid",
            "LIBRARY_EMAIL_PASSWORD": "not-a-real-password",
            "LIBRARY_EMAIL_FROM": "library@example.invalid",
            "LIBRARY_STATIC_ROOT": str(tmp_path / "static"),
            "LIBRARY_SCHEDULER_ENABLED": "0",
        }
    )
    for key in drop:
        env.pop(key, None)
    return env


def _run_python(code: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )


_SETUP_ONLY = "import django\ndjango.setup()\nprint('LOADED')\n"


def test_tc01_admin_returns_404_in_production(tmp_path: Path) -> None:
    code = (
        "import django\n"
        "django.setup()\n"
        "from django.test import Client\n"
        "response = Client().get('/admin/', HTTP_HOST='library.local', secure=True)\n"
        "print('STATUS', response.status_code)\n"
    )
    result = _run_python(code, _prod_env(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "STATUS 404" in result.stdout


def test_tc02_missing_secret_key_stops_with_named_error(tmp_path: Path) -> None:
    result = _run_python(_SETUP_ONLY, _prod_env(tmp_path, drop=("LIBRARY_SECRET_KEY",)))
    assert result.returncode != 0
    assert "LOADED" not in result.stdout
    assert (
        "ImproperlyConfigured: Eksik ortam değişkeni: LIBRARY_SECRET_KEY" in result.stderr
    )


@pytest.mark.django_db
def test_tc03_staff_password_is_stored_as_argon2id() -> None:
    from library_site.settings import base

    raw_password = "Gizli-Parola-2026"
    with override_settings(PASSWORD_HASHERS=base.PASSWORD_HASHERS):
        user = get_user_model().objects.create_user(username="ali", password=raw_password)
        stored = get_user_model().objects.get(pk=user.pk).password
        assert stored.startswith("argon2$argon2id$")
        assert raw_password not in stored
        assert get_user_model().objects.get(pk=user.pk).check_password(raw_password)
    assert base.PASSWORD_HASHERS[0] == "django.contrib.auth.hashers.Argon2PasswordHasher"


@pytest.mark.parametrize(
    ("instant", "expected"),
    [
        (datetime(2026, 11, 16, 20, 59, 59, tzinfo=dt_timezone.utc), date(2026, 11, 16)),
        (datetime(2026, 11, 16, 21, 0, 0, tzinfo=dt_timezone.utc), date(2026, 11, 17)),
    ],
)
def test_tc235_istanbul_local_date_boundary(
    monkeypatch: pytest.MonkeyPatch, instant: datetime, expected: date
) -> None:
    assert settings.TIME_ZONE == "Europe/Istanbul"
    assert settings.USE_TZ is True
    assert settings.LANGUAGE_CODE == "tr"
    ZoneInfo("Europe/Istanbul")  # must not raise ZoneInfoNotFoundError
    monkeypatch.setattr(timezone, "now", lambda: instant)
    assert timezone.localdate() == expected


def test_tc235_requirements_pin_tzdata() -> None:
    lines = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert any(line.startswith("tzdata==") for line in lines)


@pytest.mark.parametrize("missing", REQUIRED_PROD_VARS)
def test_tc236_each_required_variable_is_enforced(tmp_path: Path, missing: str) -> None:
    result = _run_python(_SETUP_ONLY, _prod_env(tmp_path, drop=(missing,)))
    assert result.returncode != 0
    assert "LOADED" not in result.stdout
    assert f"ImproperlyConfigured: Eksik ortam değişkeni: {missing}" in result.stderr


def test_tc236_scheduler_flag_defaults_to_zero(tmp_path: Path) -> None:
    code = (
        "import django\n"
        "django.setup()\n"
        "from django.conf import settings\n"
        "print('SCHEDULER', repr(settings.LIBRARY_SCHEDULER_ENABLED))\n"
    )
    result = _run_python(code, _prod_env(tmp_path, drop=("LIBRARY_SCHEDULER_ENABLED",)))
    assert result.returncode == 0, result.stderr
    assert "SCHEDULER '0'" in result.stdout


def test_adr0052_production_smtp_timeout_is_ten_seconds(tmp_path: Path) -> None:
    code = (
        "import django\n"
        "django.setup()\n"
        "from django.conf import settings\n"
        "print('TIMEOUT', repr(settings.EMAIL_TIMEOUT))\n"
    )
    result = _run_python(code, _prod_env(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "TIMEOUT 10" in result.stdout
