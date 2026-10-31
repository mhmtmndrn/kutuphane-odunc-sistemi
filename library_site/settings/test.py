"""Test settings: in-memory e-mail backend and a fast password hasher."""

import os
from pathlib import Path

_VAR_DIR = Path(__file__).resolve().parent.parent.parent / "var" / "test"

# Defaults for the variables that ``base`` reads with ``env``. The test
# database itself is in memory; tests that touch the file system use tmp_path.
os.environ.setdefault("LIBRARY_SECRET_KEY", "test-only-insecure-key")
os.environ.setdefault("LIBRARY_DB_PATH", str(_VAR_DIR / "library.sqlite3"))
os.environ.setdefault("LIBRARY_BACKUP_DIR", str(_VAR_DIR / "backups"))
os.environ.setdefault("LIBRARY_EXPORT_DIR", str(_VAR_DIR / "exports"))
os.environ.setdefault("LIBRARY_EXPORT_PASSPHRASE_FILE", str(_VAR_DIR / "export-passphrase.txt"))

from .base import *  # noqa: E402,F403

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Test-only: MD5 keeps the suite fast. The Argon2 test (NFR-06, TC-03) reads
# ``base.PASSWORD_HASHERS`` instead.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
