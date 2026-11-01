"""Helpers for the operations tests (G14–G16)."""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_HOLD_LOCK = """
import sys
from pathlib import Path
from operations.applock import hold_app_lock
handle = hold_app_lock(Path(sys.argv[1]))
print("ready", flush=True)
sys.stdin.read()
"""


def counts(db: Path) -> tuple[int, int, int]:
    """Member, copy and loan counts read with a plain SQLite connection."""
    con = sqlite3.connect(db)
    try:
        return tuple(
            con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            for table in ("member", "copy", "loan")
        )
    finally:
        con.close()


def migration_rows(db: Path) -> list[tuple[str, str]]:
    con = sqlite3.connect(db)
    try:
        return con.execute("SELECT app, name FROM django_migrations ORDER BY id").fetchall()
    finally:
        con.close()


@contextmanager
def lock_held_elsewhere(db_path: Path) -> Iterator[subprocess.Popen]:
    """Hold the application lock of ``db_path`` in a child process."""
    child = subprocess.Popen(
        [sys.executable, "-c", _HOLD_LOCK, str(db_path)],
        cwd=REPO_ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert child.stdout.readline().strip() == "ready"
        yield child
    finally:
        if child.poll() is None:
            child.kill()
        child.wait(timeout=10)
        child.stdin.close()
        child.stdout.close()


def manage(*args: str, env: dict[str, str]) -> subprocess.CompletedProcess:
    """Run ``manage.py`` in a child process with the test settings."""
    full_env = {**os.environ, "DJANGO_SETTINGS_MODULE": "library_site.settings.test", **env}
    full_env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "manage.py", *args],
        cwd=REPO_ROOT,
        env=full_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
