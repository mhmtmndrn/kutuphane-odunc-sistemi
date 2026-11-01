"""Application lock (KL-4, R-09, R-13).

``wsgi.py`` holds an operating-system lock on ``<LIBRARY_DB_PATH>.app.lock``
for the life of the process; ``restore_backup`` refuses to run while it is
held. The lock goes away with the process, so a crash leaves nothing stale.
Linux uses ``fcntl.flock``, Windows ``msvcrt.locking`` on the first byte.
This module does not import Django: tests hold the lock from a bare child
process.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import IO

if os.name == "nt":  # pragma: no cover - run in the local Windows verification
    import msvcrt

    def _lock(handle: IO[bytes]) -> None:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock(handle: IO[bytes]) -> None:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _lock(handle: IO[bytes]) -> None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock(handle: IO[bytes]) -> None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class AppLockError(RuntimeError):
    """The lock is held by another process (or another handle)."""


def lock_path(db_path: Path) -> Path:
    return Path(str(db_path) + ".app.lock")


def hold_app_lock(db_path: Path) -> IO[bytes]:
    """Take the lock without blocking and return the open handle; keep it
    referenced for as long as the lock must be held."""
    path = lock_path(db_path)
    handle = open(path, "a+b")  # noqa: SIM115 - the caller owns the handle
    try:
        _lock(handle)
    except OSError:
        handle.close()
        raise AppLockError(f"Uygulama zaten çalışıyor: {path}") from None
    return handle


def release_app_lock(handle: IO[bytes]) -> None:
    try:
        _unlock(handle)
    finally:
        handle.close()


def try_lock(db_path: Path) -> bool:
    """True if the lock is free; the lock is released again at once."""
    try:
        handle = hold_app_lock(db_path)
    except AppLockError:
        return False
    release_app_lock(handle)
    return True
