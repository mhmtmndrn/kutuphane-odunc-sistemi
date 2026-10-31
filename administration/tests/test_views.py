"""View tests for administration (G03).

TC-21, TC-23, TC-25, TC-242…TC-245; plus the settings, closed-day and audit
screens.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone as dt_timezone

import pytest
from django.test import Client
from django.utils import timezone

from accounts.models import Role
from administration import services
from administration.audit import AuditAction, record_audit
from administration.jobs import Job
from administration.models import AuditEvent, ClosedDate, JobRun, WeeklyClosedDay
from tests.support.clock import FrozenClock
from tests.support.factories import make_staff

pytestmark = pytest.mark.django_db

ISTANBUL_0406 = datetime(2026, 11, 16, 1, 6, tzinfo=dt_timezone.utc)  # 04:06 local
EXPORT_OLD = "Bina dışı yedek 7 günden eski"
EXPORT_NONE = "Bina dışı yedek henüz alınmadı"
BACKUP_FAILED = "Son günlük yedek başarısız oldu"
BACKUP_OLD = "Günlük yedek 26 saatten eski"


@pytest.fixture
def admin():
    return make_staff("ayse.y", role=Role.ADMIN, full_name="Ayşe Yılmaz")


@pytest.fixture
def admin_client(client: Client, admin) -> Client:
    client.force_login(admin)
    return client


@pytest.fixture
def clerk_client(client: Client) -> Client:
    client.force_login(make_staff("ali", role=Role.CLERK))
    return client


def _job(job: Job, status: str, *, run_on: date, started: datetime, finished=None) -> JobRun:
    return JobRun.objects.create(
        job=job, run_on=run_on, status=status, started_at=started, finished_at=finished
    )


def _logged_in(client: Client, user) -> Client:
    # Log in after freezing the clock, or the session looks expired.
    client.force_login(user)
    return client


def _body(response) -> str:
    return response.content.decode()


# --- Home page ---------------------------------------------------------------


def test_home_requires_login(client: Client) -> None:
    response = client.get("/")
    assert response.status_code == 302
    assert response["Location"] == "/giris/?next=/"


def test_home_for_clerk_has_no_admin_panel(clerk_client: Client) -> None:
    response = clerk_client.get("/")
    assert response.status_code == 200
    body = _body(response)
    assert "Son dışa aktarma" not in body
    assert 'href="/ayarlar/"' not in body


def test_home_for_admin_links_admin_screens(admin_client: Client) -> None:
    body = _body(admin_client.get("/"))
    for href in ("/ayarlar/", "/kapali-gunler/", "/denetim/"):
        assert f'href="{href}"' in body


@pytest.mark.parametrize(("days_ago", "warned"), [(7, False), (8, True)])
def test_tc25_export_age_warning(
    client: Client, admin, monkeypatch: pytest.MonkeyPatch, days_ago: int, warned: bool
) -> None:
    FrozenClock(monkeypatch, ISTANBUL_0406)
    admin_client = _logged_in(client, admin)
    run_on = timezone.localdate() - timedelta(days=days_ago)
    started = ISTANBUL_0406 - timedelta(days=days_ago)
    _job(Job.EXPORT, JobRun.Status.SUCCESS, run_on=run_on, started=started, finished=started)
    body = _body(admin_client.get("/"))
    assert run_on.strftime("%d.%m.%Y") in body
    assert (EXPORT_OLD in body) is warned


def test_tc242_failed_backup_is_shown_to_admin_only(
    client: Client, admin, monkeypatch: pytest.MonkeyPatch
) -> None:
    FrozenClock(monkeypatch, ISTANBUL_0406)
    started = ISTANBUL_0406 - timedelta(hours=2)
    _job(Job.BACKUP, JobRun.Status.FAILED, run_on=date(2026, 11, 16), started=started,
         finished=started)
    client.force_login(admin)
    assert BACKUP_FAILED in _body(client.get("/"))
    client.post("/cikis/")
    client.force_login(make_staff("ali", role=Role.CLERK))
    assert BACKUP_FAILED not in _body(client.get("/"))


def test_tc243_running_backup_is_not_the_last_finished(
    client: Client, admin, monkeypatch: pytest.MonkeyPatch
) -> None:
    FrozenClock(monkeypatch, ISTANBUL_0406)
    admin_client = _logged_in(client, admin)
    # Last success finished 2026-11-15 02:05 local (23:05 UTC on the 14th).
    finished = datetime(2026, 11, 14, 23, 5, tzinfo=dt_timezone.utc)
    _job(Job.BACKUP, JobRun.Status.SUCCESS, run_on=date(2026, 11, 15),
         started=finished - timedelta(minutes=5), finished=finished)
    _job(Job.BACKUP, JobRun.Status.RUNNING, run_on=date(2026, 11, 16),
         started=datetime(2026, 11, 15, 23, 0, tzinfo=dt_timezone.utc))
    body = _body(admin_client.get("/"))
    assert BACKUP_OLD in body
    assert BACKUP_FAILED not in body


def test_tc244_no_export_yet(admin_client: Client) -> None:
    assert EXPORT_NONE in _body(admin_client.get("/"))


def test_tc244_failed_export_after_success_keeps_success_date(
    client: Client, admin, monkeypatch: pytest.MonkeyPatch
) -> None:
    FrozenClock(monkeypatch, ISTANBUL_0406)
    admin_client = _logged_in(client, admin)
    today = timezone.localdate()
    two_days = today - timedelta(days=2)
    _job(Job.EXPORT, JobRun.Status.SUCCESS, run_on=two_days,
         started=ISTANBUL_0406 - timedelta(days=2), finished=ISTANBUL_0406 - timedelta(days=2))
    _job(Job.EXPORT, JobRun.Status.FAILED, run_on=today,
         started=ISTANBUL_0406, finished=ISTANBUL_0406)
    body = _body(admin_client.get("/"))
    assert EXPORT_OLD not in body and EXPORT_NONE not in body
    assert two_days.strftime("%d.%m.%Y") in body


def test_tc245_backup_warning_comes_before_export_warning(admin_client: Client) -> None:
    body = _body(admin_client.get("/"))
    assert "Günlük yedek henüz alınmadı" in body and EXPORT_NONE in body
    assert body.index("Günlük yedek henüz alınmadı") < body.index(EXPORT_NONE)


# --- Settings screen (FR-23, AC-22) -----------------------------------------

VALID_SETTINGS = {
    "loan_period_days": "21",
    "max_open_loans": "4",
    "daily_fine": "7,50",
    "fine_cap": "150,00",
    "debt_threshold": "50",
    "retention_years": "2",
    "library_name": "Merkez Kütüphanesi",
}


def test_settings_form_shows_current_values_in_tl(admin_client: Client) -> None:
    response = admin_client.get("/ayarlar/")
    assert response.status_code == 200
    body = _body(response)
    assert 'value="5,00"' in body and 'value="150,00"' in body
    assert 'value="Kütüphane"' in body


def test_settings_post_saves_and_redirects(admin_client: Client) -> None:
    response = admin_client.post("/ayarlar/", VALID_SETTINGS)
    assert response.status_code == 302
    assert response["Location"] == "/ayarlar/"
    settings = services.get_settings()
    assert settings.loan_period_days == 21
    assert settings.daily_fine_kurus == 750
    assert settings.debt_threshold_kurus == 5000
    assert settings.library_name == "Merkez Kütüphanesi"
    assert "Ayarlar kaydedildi" in _body(admin_client.get("/ayarlar/"))


def test_settings_post_with_bad_amount_shows_error(admin_client: Client) -> None:
    response = admin_client.post("/ayarlar/", {**VALID_SETTINGS, "daily_fine": "7.5"})
    assert response.status_code == 200
    assert response.context["form"].errors["daily_fine"]
    assert services.get_settings().daily_fine_kurus == 500


def test_settings_rule_violation_is_shown_on_the_form(admin_client: Client) -> None:
    response = admin_client.post("/ayarlar/", {**VALID_SETTINGS, "debt_threshold": "0"})
    assert response.status_code == 200
    assert response.context["form"].non_field_errors()
    assert services.get_settings().debt_threshold_kurus == 5000


def test_tc21_clerk_post_settings_is_forbidden(clerk_client: Client) -> None:
    response = clerk_client.post("/ayarlar/", VALID_SETTINGS)
    assert response.status_code == 403
    assert services.get_settings().loan_period_days == 14
    assert AuditEvent.objects.count() == 0


# --- Closed days screen (FR-24, AC-24) --------------------------------------


def test_tc23_six_days_accepted_seventh_rejected(admin_client: Client) -> None:
    response = admin_client.post("/kapali-gunler/", {"weekdays": ["0", "1", "2", "3", "4", "5"]})
    assert response.status_code == 302
    assert WeeklyClosedDay.objects.count() == 6

    response = admin_client.post(
        "/kapali-gunler/", {"weekdays": ["0", "1", "2", "3", "4", "5", "6"]}
    )
    assert response.status_code == 200
    assert "En az bir gün açık kalmalı" in _body(response)
    assert WeeklyClosedDay.objects.count() == 6


def test_closed_days_page_lists_days_and_dates(admin_client: Client, admin) -> None:
    services.set_weekly_closed(admin, {6})
    services.add_closed_date(admin, date(2027, 10, 29), "Cumhuriyet Bayramı")
    response = admin_client.get("/kapali-gunler/")
    body = _body(response)
    assert "29.10.2027" in body and "Cumhuriyet Bayramı" in body
    assert response.context["weekly_form"].initial["weekdays"] == ["6"]
    assert body.count("checked") == 1


def test_add_and_remove_closed_date(admin_client: Client) -> None:
    response = admin_client.post(
        "/kapali-gunler/tarih/", {"date": "2027-10-29", "note": "Bayram"}
    )
    assert response.status_code == 302
    closed = ClosedDate.objects.get()
    assert closed.date == date(2027, 10, 29)

    response = admin_client.post("/kapali-gunler/tarih/", {"date": "2027-10-29", "note": ""})
    assert response.status_code == 200
    assert ClosedDate.objects.count() == 1

    response = admin_client.post(f"/kapali-gunler/tarih/{closed.pk}/sil/")
    assert response.status_code == 302
    assert ClosedDate.objects.count() == 0


def test_add_closed_date_with_invalid_date_shows_error(admin_client: Client) -> None:
    response = admin_client.post("/kapali-gunler/tarih/", {"date": "yarın", "note": ""})
    assert response.status_code == 200
    assert ClosedDate.objects.count() == 0


def test_remove_missing_closed_date_shows_message(admin_client: Client) -> None:
    # Plan §4.0: a rule violation re-shows the same screen with HTTP 200.
    response = admin_client.post("/kapali-gunler/tarih/999/sil/")
    assert response.status_code == 200
    assert "administration/closed_days.html" in [t.name for t in response.templates]
    assert "Kapalı tarih bulunamadı" in _body(response)


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", "/kapali-gunler/"),
        ("post", "/kapali-gunler/"),
        ("post", "/kapali-gunler/tarih/"),
        ("post", "/kapali-gunler/tarih/1/sil/"),
        ("get", "/denetim/"),
        ("get", "/ayarlar/"),
    ],
)
def test_admin_screens_are_forbidden_for_clerk(clerk_client: Client, method: str, url: str) -> None:
    assert getattr(clerk_client, method)(url).status_code == 403


# --- Audit list (FR-26, KL-11) ----------------------------------------------


def test_audit_list_newest_first_50_per_page(admin_client: Client, admin) -> None:
    for i in range(51):
        record_audit(admin, AuditAction.FEE, "ledger_entry", i + 1, {"amount_kurus": i})
    response = admin_client.get("/denetim/")
    assert response.status_code == 200
    page = response.context["page"]
    assert len(page.object_list) == 50
    assert page.object_list[0].target_id == 51
    body = _body(response)
    assert "ayse.y" in body

    second = admin_client.get("/denetim/?sayfa=2").context["page"]
    assert [e.target_id for e in second.object_list] == [1]


def test_audit_list_shows_system_actor(admin_client: Client) -> None:
    record_audit(None, AuditAction.FEE, "ledger_entry", 1, {"amount_kurus": 100})
    assert "Sistem" in _body(admin_client.get("/denetim/"))
