"""Concurrency test support (test plan §5): a file-based temporary SQLite
database and a helper that runs callables in parallel threads.

The suite's database is in memory with a shared cache. There, SQLite's
table locks fail at once (``SQLITE_LOCKED``) instead of waiting, so
``busy_timeout`` and the IMMEDIATE transactions of ADR-0002 cannot be
tested. ``file_db`` points the ``default`` alias at a migrated file database
for one test, with the production connection options (WAL, IMMEDIATE,
``busy_timeout``), and restores the in-memory database afterwards.

Use it with ``@pytest.mark.django_db(transaction=True)``.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from django.core.management import call_command
from django.db import connections


@pytest.fixture
def file_db(tmp_path: Path, transactional_db: None) -> Iterator[Path]:
    path = tmp_path / "concurrency.sqlite3"
    original_settings = connections.settings["default"]
    original_connection = connections["default"]
    file_settings = {**original_settings, "NAME": str(path), "TEST": {}}
    connections.settings["default"] = file_settings
    connections["default"] = connections.create_connection("default")
    try:
        call_command("migrate", verbosity=0, interactive=False)
        yield path
    finally:
        connections["default"].close()
        connections.settings["default"] = original_settings
        connections["default"] = original_connection


def run_parallel(*calls: Callable[[], Any]) -> list[Any]:
    """Start every call at the same moment (``threading.Barrier``) in its own
    thread with its own database connection; return each result or the
    exception it raised, in order."""
    barrier = threading.Barrier(len(calls))
    results: list[Any] = [None] * len(calls)

    def worker(index: int, call: Callable[[], Any]) -> None:
        try:
            barrier.wait()
            results[index] = call()
        except BaseException as exc:  # noqa: BLE001 - reported to the test
            results[index] = exc
        finally:
            connections.close_all()

    threads = [threading.Thread(target=worker, args=item) for item in enumerate(calls)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    return results
