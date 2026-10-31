"""NFR-07: every admin view refuses a clerk (G04: TC-31, TC-32, TC-33).

The admin views are found from the URL resolver through the ``required_role``
attribute that ``require_role`` writes (plan G02). ``EXPECTED_ADMIN_ROUTES``
holds all 19 admin routes of plan §4.1, including those that later tasks add.
The ADMIN-guarded routes must equal the expected routes that exist today, so
an admin route added later without the ADMIN guard fails TC-32.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

import pytest
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver

from accounts.models import Role, StaffUser
from administration.models import AuditEvent, ClosedDate, LibrarySettings, WeeklyClosedDay
from tests.support.factories import make_staff

pytestmark = pytest.mark.django_db

# All 19 admin routes of plan §4.1. Routes of later tasks are checked as
# soon as they exist.
EXPECTED_ADMIN_ROUTES = {
    "personel/",
    "personel/yeni/",
    "personel/<int:pk>/",
    "personel/<int:pk>/pasif/",
    "personel/<int:pk>/parola/",
    "personel/<int:pk>/kilit-ac/",
    "ayarlar/",
    "kapali-gunler/",
    "kapali-gunler/tarih/",
    "kapali-gunler/tarih/<int:pk>/sil/",
    "denetim/",
    "uyeler/saklama/",
    "nushalar/<str:barcode>/kayip/",
    "nushalar/<str:barcode>/hasarli/",
    "nushalar/<str:barcode>/onarildi/",
    "nushalar/<str:barcode>/kayittan-dus/",
    "borclar/<int:member_no>/af/",
    "borclar/<int:member_no>/para-iadesi/",
    "borclar/<int:member_no>/iptal/",
}

# Routes that are deliberately open to every visitor.
PUBLIC_ROUTES = {"giris/", "cikis/"}

# Staff routes of plan §4.1 that must stay out of the admin set (TC-32);
# checked as soon as they exist.
CLERK_ROUTES_NOT_ADMIN = {
    "parola/",
    "nushalar/<str:barcode>/bulundu/",
    "uyeler/<int:member_no>/aktif/",
    "gecikenler/",
    "gecikenler/hatirlat/",
}

_CONVERTER = re.compile(r"<(?:(?P<kind>\w+):)?\w+>")
_SAMPLE = {"int": "1", "str": "00000001", None: "00000001"}


def _walk(patterns, prefix: str = "") -> Iterator[tuple[str, object]]:
    for entry in patterns:
        if isinstance(entry, URLResolver):
            yield from _walk(entry.url_patterns, prefix + str(entry.pattern))
        elif isinstance(entry, URLPattern):
            yield prefix + str(entry.pattern), entry.callback


def _routes() -> dict[str, object]:
    return dict(_walk(get_resolver().url_patterns))


def _admin_routes() -> set[str]:
    return {
        route
        for route, view in _routes().items()
        if getattr(view, "required_role", None) == Role.ADMIN
    }


def _url(route: str) -> str:
    return "/" + _CONVERTER.sub(lambda m: _SAMPLE[m["kind"]], route)


def _snapshot() -> tuple:
    settings = LibrarySettings.objects.get(pk=1)
    return (
        AuditEvent.objects.count(),
        ClosedDate.objects.count(),
        WeeklyClosedDay.objects.count(),
        list(StaffUser.objects.order_by("pk").values_list("username", "role", "is_active", "password")),
        settings.loan_period_days,
        settings.library_name,
    )


def test_tc31_clerk_gets_403_on_every_admin_view(client: Client) -> None:
    make_staff("ayse.y", role=Role.ADMIN)  # pk 1: a real target for <int:pk>
    client.force_login(make_staff("ali", role=Role.CLERK))
    before = _snapshot()
    routes = sorted(_admin_routes())
    assert routes, "no admin routes found"
    for route in routes:
        url = _url(route)
        assert client.get(url).status_code == 403, f"GET {url}"
        assert client.post(url, {"role": "CLERK", "password": "Kx7#mQ2vLp"}).status_code == 403, (
            f"POST {url}"
        )
    assert _snapshot() == before


def test_tc32_admin_routes_match_plan_list() -> None:
    assert len(EXPECTED_ADMIN_ROUTES) == 19
    assert not EXPECTED_ADMIN_ROUTES & CLERK_ROUTES_NOT_ADMIN
    routes = _routes()
    existing = set(routes)
    admin_routes = _admin_routes()
    assert admin_routes == EXPECTED_ADMIN_ROUTES & existing
    for route in CLERK_ROUTES_NOT_ADMIN & existing:
        assert getattr(routes[route], "required_role", None) == Role.CLERK, route


def test_every_non_public_route_is_role_checked() -> None:
    unchecked = {
        route
        for route, view in _routes().items()
        if route not in PUBLIC_ROUTES and getattr(view, "required_role", None) is None
    }
    assert unchecked == set()


def test_tc33_admin_is_not_forbidden_on_admin_views(client: Client) -> None:
    client.force_login(make_staff("ayse.y", role=Role.ADMIN))
    for route in sorted(_admin_routes()):
        url = _url(route)
        assert client.get(url).status_code != 403, f"GET {url}"
