"""Development settings: DEBUG, admin panel, console e-mail backend."""

import os
from pathlib import Path

_VAR_DIR = Path(__file__).resolve().parent.parent.parent / "var"

# Development defaults for the variables that ``base`` reads with ``env``.
os.environ.setdefault("LIBRARY_SECRET_KEY", "dev-only-insecure-key-do-not-use-in-production")
os.environ.setdefault("LIBRARY_DB_PATH", str(_VAR_DIR / "library.sqlite3"))
os.environ.setdefault("LIBRARY_BACKUP_DIR", str(_VAR_DIR / "backups"))
os.environ.setdefault("LIBRARY_EXPORT_DIR", str(_VAR_DIR / "exports"))
os.environ.setdefault("LIBRARY_EXPORT_PASSPHRASE_FILE", str(_VAR_DIR / "export-passphrase.txt"))

from .base import *  # noqa: E402,F403
from .base import INSTALLED_APPS  # noqa: E402

DEBUG = True

INSTALLED_APPS = [*INSTALLED_APPS, "django.contrib.admin"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# SQLite does not create missing parent directories.
_VAR_DIR.mkdir(exist_ok=True)
