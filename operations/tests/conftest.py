"""Fixtures for the operations tests (G14–G16).

``ops`` points the default database at a migrated temporary file (``file_db``)
and the backup and export folders at paths with spaces and Turkish letters
(test plan §5, TC-189). Commands run in autocommit mode, as in production.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from tests.support.concurrency import file_db  # noqa: F401

# Small scrypt cost so that command tests stay fast; TC-192 checks the real
# parameters (phase 4 small decision 6).
FAST_KDF = {"n": 2**10, "r": 8, "p": 1}
PASSPHRASE = "gizli parola"


@dataclass
class Ops:
    db: Path
    backups: Path
    exports: Path
    passphrase_file: Path


@pytest.fixture
def ops(file_db: Path, tmp_path: Path, settings, monkeypatch: pytest.MonkeyPatch) -> Ops:  # noqa: F811
    from operations import backup

    root = tmp_path / "Yedek Klasörü Ğüş"
    backups = root / "günlük yedek"
    exports = root / "dışa aktarma"
    backups.mkdir(parents=True)
    exports.mkdir()
    passphrase_file = root / "parola dosyası.txt"
    passphrase_file.write_text(PASSPHRASE + "\n", encoding="utf-8")
    settings.LIBRARY_BACKUP_DIR = str(backups)
    settings.LIBRARY_EXPORT_DIR = str(exports)
    settings.LIBRARY_EXPORT_PASSPHRASE_FILE = str(passphrase_file)
    monkeypatch.setattr(backup, "KDF_PARAMS", FAST_KDF)
    return Ops(file_db, backups, exports, passphrase_file)
