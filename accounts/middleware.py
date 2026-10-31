"""Send staff with a pending password change to ``/parola/`` (ADR-0043, KL-32)."""

from __future__ import annotations

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

PASSWORD_CHANGE_PATH = "/parola/"
EXEMPT_PATHS = frozenset({PASSWORD_CHANGE_PATH, "/cikis/"})


class ForcePasswordChangeMiddleware:
    """Placed after ``AuthenticationMiddleware``. Exempt: ``/parola/``, ``/cikis/``, static."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = request.user
        if (
            user.is_authenticated
            and user.must_change_password
            and not self._is_exempt(request.path_info)
        ):
            return redirect(PASSWORD_CHANGE_PATH)
        return self.get_response(request)

    @staticmethod
    def _is_exempt(path: str) -> bool:
        return path in EXEMPT_PATHS or path.startswith(settings.STATIC_URL)
