"""Application lock (KL-4, R-13): TC-302. Runs on Linux (``fcntl``) in the
cloud and on Windows (``msvcrt``) in the local verification (R-15)."""

from __future__ import annotations

from pathlib import Path

import pytest

from operations import applock
from operations.tests.support import lock_held_elsewhere


def test_tc302_lock_held_by_another_process(tmp_path: Path) -> None:
    db = tmp_path / "Kütüphane veri" / "library.sqlite3"
    db.parent.mkdir()
    with lock_held_elsewhere(db) as child:
        assert applock.try_lock(db) is False
        child.kill()
        child.wait(timeout=10)
        assert applock.try_lock(db) is True
    assert applock.lock_path(db) == Path(str(db) + ".app.lock")


def test_hold_raises_with_the_lock_path(tmp_path: Path) -> None:
    db = tmp_path / "library.sqlite3"
    handle = applock.hold_app_lock(db)
    try:
        with pytest.raises(applock.AppLockError) as info:
            applock.hold_app_lock(db)
        assert isinstance(info.value, RuntimeError)
        assert str(info.value) == f"Uygulama zaten çalışıyor: {db}.app.lock"
        assert applock.try_lock(db) is False
    finally:
        applock.release_app_lock(handle)
    assert applock.try_lock(db) is True
    # try_lock leaves the lock free.
    applock.release_app_lock(applock.hold_app_lock(db))
