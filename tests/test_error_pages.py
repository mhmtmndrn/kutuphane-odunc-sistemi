"""NFR-09: error pages are Turkish only (B10: TC-367, TC-368).

Without project templates Django's ``django.views.defaults`` pages are fixed
English text ("Not Found", "403 Forbidden", ...) that does not go through
gettext. TC-367 renders each default handler directly; TC-368 reaches the
404 and 403 pages through real application paths with ``DEBUG=False``.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404, HttpRequest, HttpResponse
from django.test import Client, RequestFactory
from django.views import defaults

from accounts.models import Role
from tests.support.factories import make_staff

ENGLISH_DEFAULTS = ("Not Found", "Forbidden", "Bad Request", "Server Error", "requested resource")


def _bad_request(request: HttpRequest) -> HttpResponse:
    return defaults.bad_request(request, SuspiciousOperation("test"))


def _permission_denied(request: HttpRequest) -> HttpResponse:
    return defaults.permission_denied(request, PermissionDenied("test"))


def _page_not_found(request: HttpRequest) -> HttpResponse:
    return defaults.page_not_found(request, Http404("test"))


def _server_error(request: HttpRequest) -> HttpResponse:
    return defaults.server_error(request)


def _assert_turkish(body: str, title: str) -> None:
    assert 'lang="tr"' in body
    assert title in body
    for text in ENGLISH_DEFAULTS:
        assert text not in body, text


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("handler", "status", "title"),
    [
        (_bad_request, 400, "Geçersiz istek"),
        (_permission_denied, 403, "Erişim izni yok"),
        (_page_not_found, 404, "Sayfa bulunamadı"),
        (_server_error, 500, "Sunucu hatası"),
    ],
    ids=["400", "403", "404", "500"],
)
def test_tc367_default_error_pages_are_turkish(
    rf: RequestFactory,
    handler: Callable[[HttpRequest], HttpResponse],
    status: int,
    title: str,
) -> None:
    request = rf.get("/yok/")
    request.user = AnonymousUser()

    response = handler(request)

    assert response.status_code == status
    _assert_turkish(response.content.decode(), title)


@pytest.mark.django_db
def test_tc367_csrf_failure_page_is_turkish() -> None:
    """Django's own CSRF page hard-codes ``lang="en"`` and "403 Forbidden"."""
    client = Client(enforce_csrf_checks=True)

    response = client.post("/giris/", {"username": "x", "password": "y"})

    assert response.status_code == 403
    _assert_turkish(response.content.decode(), "Form güvenlik kontrolünden geçemedi")


@pytest.mark.django_db
def test_tc368_missing_member_shows_turkish_404(client: Client) -> None:
    client.force_login(make_staff("ali", role=Role.CLERK))

    response = client.get("/uyeler/999999/")

    assert response.status_code == 404
    body = response.content.decode()
    _assert_turkish(body, "Sayfa bulunamadı")
    assert "Çıkış" in body  # rendered with the request: the staff menu is shown


@pytest.mark.django_db
def test_tc368_clerk_on_admin_path_shows_turkish_403(client: Client) -> None:
    client.force_login(make_staff("ali", role=Role.CLERK))

    response = client.get("/personel/")

    assert response.status_code == 403
    _assert_turkish(response.content.decode(), "Erişim izni yok")
