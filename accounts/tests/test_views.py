"""View-level tests for login, logout, session expiry and lockout (G02).

TC-04, TC-05, TC-09 and TC-10 need a staff page; ``/odunc/`` arrives in G11,
so they use the test-only URLconf (plan §11, G02 (a)).
"""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

import pytest
from django.contrib.auth import SESSION_KEY
from django.http import HttpRequest, HttpResponse
from django.test import Client
from django.urls import path

from accounts.models import Role
from accounts.permissions import require_role, staff_view
from tests.support.clock import FrozenClock
from tests.support.factories import DEFAULT_PASSWORD, make_staff

pytestmark = pytest.mark.django_db

LOCKOUT_MESSAGE = "Hesap geçici olarak kilitlendi. 15 dakika sonra yeniden deneyin."
WRONG_PASSWORD = "Yanlis-Parola-99"
START = datetime(2026, 11, 16, 9, 0, 0, tzinfo=dt_timezone.utc)


def _login(client: Client, password: str, username: str = "ali") -> HttpResponse:
    return client.post("/giris/", {"username": username, "password": password})


def _fail(client: Client, times: int, username: str = "ali") -> None:
    for _ in range(times):
        response = _login(client, WRONG_PASSWORD, username)
        assert response.status_code in (200, 429)


def _is_logged_in(client: Client) -> bool:
    return SESSION_KEY in client.session


# --- Login page --------------------------------------------------------------


def test_login_page_is_turkish_form(client: Client) -> None:
    response = client.get("/giris/")
    assert response.status_code == 200
    assert "registration/login.html" in [t.name for t in response.templates]
    body = response.content.decode()
    assert '<html lang="tr">' in body
    assert 'name="username"' in body and "autofocus" in body
    assert "csrfmiddlewaretoken" in body


def test_wrong_password_shows_form_error_with_200(client: Client) -> None:
    make_staff("ali")
    response = _login(client, WRONG_PASSWORD)
    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    assert not _is_logged_in(client)


# --- TC-04, TC-05: session required, login and logout ------------------------


@pytest.mark.urls("tests.support.urls")
def test_tc04_anonymous_request_redirects_to_login(client: Client) -> None:
    response = client.get("/odunc/")
    assert response.status_code == 302
    assert response["Location"] == "/giris/?next=/odunc/"


@pytest.mark.urls("tests.support.urls")
def test_tc05_login_then_logout_then_redirect(client: Client) -> None:
    make_staff("ali")
    response = _login(client, DEFAULT_PASSWORD)
    assert response.status_code == 302
    assert _is_logged_in(client)
    assert client.get("/odunc/").status_code == 200

    response = client.post("/cikis/")
    assert response.status_code == 302
    assert response["Location"] == "/giris/"
    assert not _is_logged_in(client)

    response = client.get("/odunc/")
    assert response.status_code == 302
    assert response["Location"] == "/giris/?next=/odunc/"


def test_logout_is_post_only(client: Client) -> None:
    client.force_login(make_staff("ali"))
    assert client.get("/cikis/").status_code == 405
    assert _is_logged_in(client)


# --- TC-06, TC-07, TC-08: lockout (ADR-0009, ADR-0049, ADR-0050) ------------


def test_tc06_successful_login_resets_failure_counter(client: Client) -> None:
    make_staff("ali")
    _fail(client, 4)
    assert _login(client, DEFAULT_PASSWORD).status_code == 302
    client.post("/cikis/")
    _fail(client, 4)
    assert _login(client, DEFAULT_PASSWORD).status_code == 302
    assert _is_logged_in(client)


def test_tc07_fifth_failure_locks_the_account(client: Client) -> None:
    make_staff("ali")
    _fail(client, 5)
    response = _login(client, DEFAULT_PASSWORD)
    assert response.status_code == 429
    assert "registration/login.html" in [t.name for t in response.templates]
    body = response.content.decode()
    assert LOCKOUT_MESSAGE in body
    assert 'name="password"' in body
    assert not _is_logged_in(client)


def test_tc07_lockout_is_per_username(client: Client) -> None:
    make_staff("ali")
    make_staff("veli")
    _fail(client, 5, "ali")
    assert _login(client, DEFAULT_PASSWORD, "veli").status_code == 302


def test_tc08_still_locked_at_14_minutes_59_seconds(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = FrozenClock(monkeypatch, START)
    make_staff("ali")
    _fail(client, 5)
    # Attempts during the lockout do not extend it (ADR-0050).
    clock.advance(minutes=10)
    _fail(client, 2)
    clock.advance(minutes=4, seconds=59)
    response = _login(client, DEFAULT_PASSWORD)
    assert response.status_code == 429
    assert LOCKOUT_MESSAGE in response.content.decode()
    assert not _is_logged_in(client)


def test_tc08_unlocked_at_15_minutes_01_second(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = FrozenClock(monkeypatch, START)
    make_staff("ali")
    _fail(client, 5)
    # Attempts during the lockout do not extend it (ADR-0050).
    clock.advance(minutes=10)
    _fail(client, 2)
    clock.advance(minutes=5, seconds=1)
    response = _login(client, DEFAULT_PASSWORD)
    assert response.status_code == 302
    assert _is_logged_in(client)


# --- TC-09, TC-10: 30-minute idle session (FR-27, architecture §6.1) --------


@pytest.mark.urls("tests.support.urls")
def test_tc09_session_alive_at_29_minutes_59_seconds(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = FrozenClock(monkeypatch, START)
    client.force_login(make_staff("ali"))
    assert client.get("/odunc/").status_code == 200
    clock.advance(minutes=29, seconds=59)
    assert client.get("/odunc/").status_code == 200


@pytest.mark.urls("tests.support.urls")
def test_tc09_session_expired_at_30_minutes_01_second(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = FrozenClock(monkeypatch, START)
    client.force_login(make_staff("ali"))
    assert client.get("/odunc/").status_code == 200
    clock.advance(minutes=30, seconds=1)
    response = client.get("/odunc/")
    assert response.status_code == 302
    assert response["Location"] == "/giris/?next=/odunc/"


@pytest.mark.urls("tests.support.urls")
def test_tc10_each_request_renews_the_session(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = FrozenClock(monkeypatch, START)
    client.force_login(make_staff("ali"))
    for _ in range(3):
        clock.advance(minutes=25)
        assert client.get("/odunc/").status_code == 200


# --- require_role / staff_view on views (FR-22) ------------------------------


@require_role(Role.ADMIN)
def _admin_view(request: HttpRequest, pk: int) -> HttpResponse:
    # Reached only after the role check, so an unknown pk cannot turn 403 into 404.
    return HttpResponse(f"admin {pk}")


@staff_view
def _clerk_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("staff")


urlpatterns = [
    path("yonetici/<int:pk>/", _admin_view),
    path("personel-sayfasi/", _clerk_view),
]

_THIS_URLCONF = __name__


@pytest.mark.urls(_THIS_URLCONF)
def test_admin_view_denies_clerk_before_object_lookup(client: Client) -> None:
    client.force_login(make_staff("ali", role=Role.CLERK))
    assert client.get("/yonetici/999/").status_code == 403
    assert client.post("/yonetici/999/").status_code == 403


@pytest.mark.urls(_THIS_URLCONF)
def test_admin_view_allows_admin(client: Client) -> None:
    client.force_login(make_staff("ayse", role=Role.ADMIN))
    response = client.get("/yonetici/7/")
    assert response.status_code == 200
    assert response.content == b"admin 7"


@pytest.mark.urls(_THIS_URLCONF)
def test_admin_view_redirects_anonymous_to_login(client: Client) -> None:
    response = client.get("/yonetici/7/")
    assert response.status_code == 302
    assert response["Location"] == "/giris/?next=/yonetici/7/"


@pytest.mark.urls(_THIS_URLCONF)
@pytest.mark.parametrize("role", [Role.CLERK, Role.ADMIN])
def test_staff_view_allows_every_role(client: Client, role: Role) -> None:
    client.force_login(make_staff("ali", role=role))
    assert client.get("/personel-sayfasi/").status_code == 200


@pytest.mark.urls(_THIS_URLCONF)
def test_staff_view_redirects_anonymous_to_login(client: Client) -> None:
    response = client.get("/personel-sayfasi/")
    assert response.status_code == 302
    assert response["Location"] == "/giris/?next=/personel-sayfasi/"


def test_view_wrappers_carry_required_role() -> None:
    assert _admin_view.required_role == Role.ADMIN
    assert _clerk_view.required_role == Role.CLERK


# =============================================================================
# G04: staff screens and forced password change (FR-21, FR-41, KL-32, KL-45)
# =============================================================================

NEW_PASSWORD = "Yeni-Parola-2026"


def _staff_events():
    from administration.models import AuditEvent

    return list(AuditEvent.objects.filter(action="STAFF_CHANGED").order_by("id"))


@pytest.fixture
def admin_user():
    return make_staff("ayse.y", role=Role.ADMIN, full_name="Ayşe Yılmaz")


@pytest.fixture
def admin_client(admin_user) -> Client:
    client = Client()
    client.force_login(admin_user)
    return client


def test_staff_list_shows_accounts(admin_client: Client) -> None:
    make_staff("ali", full_name="Ali Yılmaz")
    response = admin_client.get("/personel/")
    assert response.status_code == 200
    body = response.content.decode()
    assert "ali" in body and "Ali Yılmaz" in body and "Görevli" in body


def test_create_staff_screen(admin_client: Client) -> None:
    assert admin_client.get("/personel/yeni/").status_code == 200
    response = admin_client.post(
        "/personel/yeni/",
        {
            "username": "ali",
            "full_name": "Ali Yılmaz",
            "role": "CLERK",
            "password1": NEW_PASSWORD,
            "password2": NEW_PASSWORD,
        },
    )
    assert response.status_code == 302
    from accounts.models import StaffUser

    ali = StaffUser.objects.get(username="ali")
    assert response["Location"] == f"/personel/{ali.pk}/"
    assert ali.must_change_password is True


def test_create_staff_screen_rejects_mismatch_and_short_password(admin_client: Client) -> None:
    data = {"username": "ali", "full_name": "Ali", "role": "CLERK"}
    response = admin_client.post(
        "/personel/yeni/", {**data, "password1": NEW_PASSWORD, "password2": NEW_PASSWORD + "x"}
    )
    assert response.status_code == 200
    assert response.context["form"].errors
    response = admin_client.post(
        "/personel/yeni/", {**data, "password1": "Kx7#mQ2vL", "password2": "Kx7#mQ2vL"}
    )
    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    assert _staff_events() == []


def test_staff_detail_changes_role(admin_client: Client) -> None:
    ali = make_staff("ali")
    assert admin_client.get(f"/personel/{ali.pk}/").status_code == 200
    response = admin_client.post(f"/personel/{ali.pk}/", {"role": "ADMIN"})
    assert response.status_code == 302
    ali.refresh_from_db()
    assert ali.role == Role.ADMIN


def test_staff_detail_shows_last_admin_error(admin_client: Client, admin_user) -> None:
    response = admin_client.post(f"/personel/{admin_user.pk}/", {"role": "CLERK"})
    assert response.status_code == 200
    assert "En az bir aktif yönetici kalmalı" in response.content.decode()


def test_staff_detail_unknown_pk_is_404_for_admin(admin_client: Client) -> None:
    assert admin_client.get("/personel/999/").status_code == 404
    assert admin_client.post("/personel/999/pasif/").status_code == 404


def test_self_deactivation_message(admin_client: Client, admin_user) -> None:
    # Plan §4.0: a rule violation re-shows the same screen with HTTP 200.
    response = admin_client.post(f"/personel/{admin_user.pk}/pasif/")
    assert response.status_code == 200
    assert "accounts/staff_form.html" in [t.name for t in response.templates]
    assert "Kendi hesabınızı pasifleştiremezsiniz" in response.content.decode()
    admin_user.refresh_from_db()
    assert admin_user.is_active


def test_reset_password_screen(admin_client: Client) -> None:
    ali = make_staff("ali")
    response = admin_client.post(f"/personel/{ali.pk}/parola/", {"password": NEW_PASSWORD})
    assert response.status_code == 302
    ali.refresh_from_db()
    assert ali.check_password(NEW_PASSWORD) and ali.must_change_password


def test_reset_password_screen_rejects_short_password(admin_client: Client) -> None:
    ali = make_staff("ali")
    response = admin_client.post(f"/personel/{ali.pk}/parola/", {"password": "Kx7#mQ2vL"})
    assert response.status_code == 200
    ali.refresh_from_db()
    assert ali.check_password(DEFAULT_PASSWORD)


def test_tc28_deactivated_staff_cannot_log_in(admin_client: Client) -> None:
    ali = make_staff("ali")
    response = admin_client.post(f"/personel/{ali.pk}/pasif/")
    assert response.status_code == 302
    ali.refresh_from_db()
    assert ali.is_active is False
    assert _staff_events()[-1].details == {"change": "deactivated"}

    other = Client()
    response = _login(other, DEFAULT_PASSWORD)
    assert response.status_code == 200
    assert not _is_logged_in(other)


def test_tc30_unlock_lets_staff_log_in_at_once(admin_client: Client) -> None:
    ali = make_staff("ali")
    desk = Client()
    _fail(desk, 5)
    assert _login(desk, DEFAULT_PASSWORD).status_code == 429
    response = admin_client.post(f"/personel/{ali.pk}/kilit-ac/")
    assert response.status_code == 302
    assert _login(desk, DEFAULT_PASSWORD).status_code == 302
    assert _is_logged_in(desk)


@pytest.mark.urls("tests.support.urls")
def test_tc237_deactivation_ends_open_session(admin_client: Client) -> None:
    ali = make_staff("ali")
    desk = Client()
    desk.force_login(ali)
    assert desk.get("/odunc/").status_code == 200
    admin_client.post(f"/personel/{ali.pk}/pasif/")
    response = desk.get("/odunc/")
    assert response.status_code == 302
    assert response["Location"] == "/giris/?next=/odunc/"


@pytest.mark.urls("tests.support.urls")
def test_tc248_reset_password_forces_change_on_first_login(admin_client: Client) -> None:
    ali = make_staff("ali")
    admin_client.post(f"/personel/{ali.pk}/parola/", {"password": NEW_PASSWORD})

    desk = Client()
    assert _login(desk, NEW_PASSWORD).status_code == 302
    response = desk.get("/odunc/")
    assert response.status_code == 302
    assert response["Location"] == "/parola/"

    response = desk.post(
        "/parola/",
        {
            "old_password": NEW_PASSWORD,
            "new_password1": "Baska-Parola-2027",
            "new_password2": "Baska-Parola-2027",
        },
        follow=True,
    )
    assert response.redirect_chain == [("/", 302)]
    assert "Parolanız değiştirildi" in response.content.decode()
    assert desk.get("/odunc/").status_code == 200


@pytest.mark.urls("tests.support.urls")
def test_tc249_change_own_password_keeps_session(client: Client) -> None:
    ali = make_staff("ali")
    client.force_login(ali)
    assert client.get("/parola/").status_code == 200
    response = client.post(
        "/parola/",
        {"old_password": DEFAULT_PASSWORD, "new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD},
    )
    assert response.status_code == 302 and response["Location"] == "/"
    ali.refresh_from_db()
    assert ali.check_password(NEW_PASSWORD)
    assert client.get("/odunc/").status_code == 200
    event = _staff_events()[-1]
    assert event.actor == ali and event.details == {"change": "password_changed"}


def test_tc249_wrong_current_password_changes_nothing(client: Client) -> None:
    ali = make_staff("ali", must_change_password=True)
    client.force_login(ali)
    response = client.post(
        "/parola/",
        {"old_password": "Yanlis-Parola-99", "new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD},
    )
    assert response.status_code == 200
    assert response.context["form"].errors["old_password"]
    ali.refresh_from_db()
    assert ali.check_password(DEFAULT_PASSWORD)
    assert ali.must_change_password is True
    assert _staff_events() == []


def test_tc250_exempt_paths_are_not_redirected(client: Client, settings) -> None:
    client.force_login(make_staff("ali", must_change_password=True))
    assert client.get("/parola/").status_code == 200
    static = client.get(f"{settings.STATIC_URL}css/app.css")
    assert static.get("Location") != "/parola/"
    response = client.post("/cikis/")
    assert response.status_code == 302
    assert response["Location"] == "/giris/"


def test_flagged_session_is_redirected_from_other_pages(client: Client) -> None:
    client.force_login(make_staff("ali", must_change_password=True))
    response = client.get("/")
    assert response.status_code == 302
    assert response["Location"] == "/parola/"


def test_unflagged_and_anonymous_requests_pass(client: Client) -> None:
    assert client.get("/giris/").status_code == 200
    client.force_login(make_staff("ali"))
    assert client.get("/").status_code == 200


@pytest.mark.parametrize(("password", "accepted"), [("Kx7#mQ2vL", False), ("Kx7#mQ2vLp", True)])
def test_tc251_new_password_length(client: Client, password: str, accepted: bool) -> None:
    ali = make_staff("ali", must_change_password=True)
    client.force_login(ali)
    response = client.post(
        "/parola/",
        {"old_password": DEFAULT_PASSWORD, "new_password1": password, "new_password2": password},
    )
    ali.refresh_from_db()
    assert ali.must_change_password is (not accepted)
    assert response.status_code == (302 if accepted else 200)
