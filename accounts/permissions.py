"""Role checks for services and views (FR-22, NFR-07, plan G02).

``require_role`` wraps both kinds of callables:

- A view receives an ``HttpRequest`` first. An anonymous request goes to the
  login page; a wrong role gets ``PermissionDenied`` (403). The check runs
  before the view body, so URL arguments are never looked up for an
  unauthorized user and a missing object cannot turn 403 into 404.
- A service receives ``actor: StaffUser`` first and raises ``PermissionDenied``
  for a missing, inactive or under-privileged actor.

The wrapper exposes ``required_role``; the NFR-07 test reads it from the URL
resolver (G04).
"""

from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from .models import Role

F = TypeVar("F", bound=Callable[..., Any])


def _check_role(user: Any, role: Role) -> None:
    if not getattr(user, "is_authenticated", False) or not user.is_active:
        raise PermissionDenied
    if role == Role.ADMIN and user.role != Role.ADMIN:
        raise PermissionDenied


def require_role(role: Role) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(first: Any, *args: Any, **kwargs: Any) -> Any:
            if isinstance(first, HttpRequest):
                if not first.user.is_authenticated:
                    return redirect_to_login(first.get_full_path())
                _check_role(first.user, role)
            else:
                _check_role(first, role)
            return func(first, *args, **kwargs)

        wrapper.required_role = role  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator


def staff_view(view: F) -> F:
    """Any active staff member: ``login_required`` plus ``require_role(Role.CLERK)``.

    ``require_role`` already sends anonymous requests to the login page, so a
    single wrapper covers both and keeps ``required_role`` on the outermost
    callable.
    """
    return require_role(Role.CLERK)(view)
