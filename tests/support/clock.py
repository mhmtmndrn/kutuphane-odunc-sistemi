"""Frozen wall clock for tests that depend on elapsed time (test plan §5).

Patches every ``now`` that sessions and django-axes read, so login lockout
and session expiry can be tested without real waiting (plan §11, G02 (e)).
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

_PATCH_TARGETS = (
    "django.utils.timezone.now",
    "axes.attempts.now",
    "axes.handlers.proxy.now",
)


class FrozenClock:
    """A clock that only moves when ``advance`` is called."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, start: datetime) -> None:
        if start.tzinfo is None:
            raise ValueError("start must be timezone-aware")
        self.current = start
        for target in _PATCH_TARGETS:
            monkeypatch.setattr(target, self.now)

    def now(self) -> datetime:
        return self.current

    def advance(self, **delta: float) -> datetime:
        self.current += timedelta(**delta)
        return self.current
