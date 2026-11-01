"""Daily backup, encrypted weekly export and restore (G14; FR-28, FR-37,
NFR-03, NFR-04; ADR-0002, ADR-0006, ADR-0011, ADR-0054; KL-4, KL-14, KL-24).

Backups and exports are written to a ``.tmp`` file in the target folder and
moved into place with ``os.replace``; on failure the ``.tmp`` is removed and
an older file of the same name stays as it was (G14–G16 small decision 4).
The backup reads the database through its own SQLite connection: SQLite's
backup API waits forever on a source connection that is inside a
transaction, and a separate reader sees only committed data (TC-190).
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from django.conf import settings
from django.db import connections
from django.utils import timezone

from . import applock, domain, libx

# scrypt cost of new exports (phase 4 small decision 6); tests lower it.
KDF_PARAMS = {"n": 2**17, "r": 8, "p": 1}

# Indirection so tests can make the final move fail (TC-328).
_replace = os.replace

_SIDE_FILES = ("-journal", "-wal", "-shm")


class OperationError(Exception):
    """An expected failure; the message is shown to the user as it is."""


@dataclass(frozen=True)
class BackupResult:
    path: Path
    deleted: list[str]


@dataclass(frozen=True)
class ExportResult:
    path: Path
    source: str
    deleted: list[str]


@dataclass(frozen=True)
class RestoreCounts:
    members: int
    copies: int
    loans: int


@dataclass(frozen=True)
class RestoreResult:
    counts: RestoreCounts
    pre_restore: Path | None  # ADR-0054


def db_path() -> Path:
    return Path(connections["default"].settings_dict["NAME"])


def _remove(path: Path, *, side_files_only: bool = False) -> None:
    suffixes = _SIDE_FILES if side_files_only else ("", *_SIDE_FILES)
    for suffix in suffixes:
        Path(str(path) + suffix).unlink(missing_ok=True)


def _write_atomic(target: Path, write: Callable[[Path], None]) -> None:
    tmp = target.with_name(target.name + ".tmp")
    _remove(tmp)
    try:
        write(tmp)
        _replace(tmp, target)
    except BaseException:
        _remove(tmp)
        raise


def _copy_database(source: Path, target: Path) -> None:
    # mode=rw: a missing database is an error, not a new empty file.
    src = sqlite3.connect(f"{source.as_uri()}?mode=rw", uri=True, timeout=5)
    try:
        dst = sqlite3.connect(target)
        try:
            src.backup(dst)
            # A self-contained single file: no -wal next to the backup.
            dst.execute("PRAGMA journal_mode=DELETE")
        finally:
            dst.close()
    finally:
        src.close()


def _existing_folder(value: str, message: str) -> Path:
    folder = Path(value)
    if not folder.is_dir():
        raise OperationError(f"{message}: {folder}")
    return folder


def backup_db(run_on: date) -> BackupResult:
    """Write ``library-YYYYMMDD.sqlite3``, then delete backups older than 30
    days (KL-14). Old files are deleted only after a successful backup."""
    folder = _existing_folder(settings.LIBRARY_BACKUP_DIR, "Yedek klasörü bulunamadı")
    target = folder / domain.backup_name(run_on)
    source = db_path()
    _write_atomic(target, lambda tmp: _copy_database(source, tmp))
    deleted = domain.backups_to_delete(os.listdir(folder), run_on)
    for name in deleted:
        (folder / name).unlink()
    return BackupResult(target, deleted)


def read_passphrase(path: Path) -> str:
    try:
        text = path.read_bytes().decode("utf-8-sig")
    except FileNotFoundError:
        raise OperationError(f"Parola dosyası bulunamadı: {path}") from None
    try:
        return domain.passphrase_from_text(text)
    except ValueError:
        raise OperationError(f"Parola dosyası boş: {path}") from None


def _write_bytes(path: Path, data: bytes) -> None:
    with open(path, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def export_backup(run_on: date, passphrase_file: Path) -> ExportResult:
    """Encrypt the newest daily backup into ``library-export-YYYYMMDD.libx``,
    then delete exports older than 56 days (KL-14, KL-24)."""
    passphrase = read_passphrase(passphrase_file)
    backups = Path(settings.LIBRARY_BACKUP_DIR)
    source = domain.latest_backup(os.listdir(backups) if backups.is_dir() else [])
    if source is None:
        raise OperationError(f"Günlük yedek bulunamadı: {backups}")
    folder = _existing_folder(settings.LIBRARY_EXPORT_DIR, "Dışa aktarma klasörü bulunamadı")
    blob = libx.encrypt((backups / source).read_bytes(), passphrase, **KDF_PARAMS)
    target = folder / domain.export_name(run_on)
    _write_atomic(target, lambda tmp: _write_bytes(tmp, blob))
    deleted = domain.exports_to_delete(os.listdir(folder), run_on)
    for name in deleted:
        (folder / name).unlink()
    return ExportResult(target, source, deleted)


def _validate(candidate: Path, shown: Path) -> RestoreCounts:
    invalid = OperationError(f"Geçerli bir veritabanı yedeği değil: {shown}")
    con = sqlite3.connect(candidate)
    try:
        if con.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise invalid
        has_migrations = con.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'django_migrations'"
        ).fetchone()
        if has_migrations is None:
            raise invalid
        return RestoreCounts(
            *(
                con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                for table in ("member", "copy", "loan")
            )
        )
    except sqlite3.DatabaseError:
        raise invalid from None
    finally:
        con.close()


def _move_aside(db: Path) -> Path | None:
    """Rename the database and its -wal/-shm to ``<db>.pre-restore-<stamp>``
    without reading them (ADR-0054); a corrupt file is moved the same way."""
    suffixes = ("", "-wal", "-shm")
    if not any(Path(str(db) + suffix).exists() for suffix in suffixes):
        return None
    stamp = timezone.localtime().strftime("%Y%m%d-%H%M%S")
    base, number = f"{db}.pre-restore-{stamp}", 1
    while any(Path(base + suffix).exists() for suffix in suffixes):
        number += 1
        base = f"{db}.pre-restore-{stamp}-{number}"
    for suffix in suffixes:
        if Path(str(db) + suffix).exists():
            os.rename(str(db) + suffix, base + suffix)
    return Path(base)


def restore(path: Path, passphrase_file: Path | None) -> RestoreResult:
    """Plan G14 restore steps 1–6 with ADR-0054. No migrations are run
    (G14–G16 small decision 3)."""
    if not path.is_file():
        raise OperationError(f"Dosya bulunamadı: {path}")
    db = db_path()
    try:
        lock = applock.hold_app_lock(db)
    except applock.AppLockError:
        raise OperationError("Uygulama çalışıyor; önce servisi durdurun") from None
    try:
        data = path.read_bytes()
        if libx.is_libx(data):
            key_file = passphrase_file or Path(settings.LIBRARY_EXPORT_PASSPHRASE_FILE)
            data = libx.decrypt(data, read_passphrase(key_file))
        # Same folder as the database, so the final os.replace is atomic.
        handle, name = tempfile.mkstemp(dir=db.parent, prefix=db.name + ".restore-", suffix=".tmp")
        os.close(handle)
        tmp = Path(name)
        try:
            _write_bytes(tmp, data)
            counts = _validate(tmp, path)
            _remove(tmp, side_files_only=True)
            connections.close_all()
            pre_restore = _move_aside(db)
            _replace(tmp, db)
        except BaseException:
            _remove(tmp)
            raise
    finally:
        applock.release_app_lock(lock)
    return RestoreResult(counts, pre_restore)
