"""Service tests for administration (G03).

TC-18…TC-20, TC-22, TC-24, TC-26, TC-246; plus the audit helper and the job
run log (KL-1, KL-33).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone as dt_timezone

import pytest
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.test.utils import CaptureQueriesContext

from accounts.models import Role
from administration import jobs, services
from administration.audit import AuditAction, record_audit
from administration.errors import RuleViolation
from administration.models import AuditEvent, ClosedDate, JobRun, LibrarySettings, WeeklyClosedDay
from tests.support.clock import FrozenClock
from tests.support.factories import make_staff

pytestmark = pytest.mark.django_db

SUNDAY = 6


@pytest.fixture
def admin():
    return make_staff("ayse.y", role=Role.ADMIN, full_name="Ayşe Yılmaz")


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK)


# --- Settings ----------------------------------------------------------------


def test_default_settings_row_exists_with_documented_defaults() -> None:
    settings = services.get_settings()
    assert settings.pk == 1
    assert (settings.loan_period_days, settings.max_open_loans) == (14, 3)
    assert (settings.daily_fine_kurus, settings.fine_cap_kurus) == (500, 15000)
    assert (settings.debt_threshold_kurus, settings.retention_years) == (5000, 2)
    assert settings.library_name == "Kütüphane"
    assert LibrarySettings.objects.count() == 1


def test_tc18_admin_updates_settings_and_audit_holds_old_and_new(admin) -> None:
    services.update_settings(
        admin,
        loan_period_days=21,
        max_open_loans=4,
        daily_fine_kurus=750,
        library_name="Merkez Kütüphanesi",
    )
    settings = services.get_settings()
    assert settings.loan_period_days == 21
    assert settings.max_open_loans == 4
    assert settings.daily_fine_kurus == 750
    assert settings.library_name == "Merkez Kütüphanesi"
    assert settings.updated_by == admin
    assert settings.updated_at is not None

    event = AuditEvent.objects.get()
    assert event.action == AuditAction.SETTINGS_CHANGED
    assert event.actor == admin
    assert (event.target_type, event.target_id) == ("library_settings", 1)
    assert event.details == {
        "loan_period_days": {"old": 14, "new": 21},
        "max_open_loans": {"old": 3, "new": 4},
        "daily_fine_kurus": {"old": 500, "new": 750},
        "library_name": {"old": "Kütüphane", "new": "Merkez Kütüphanesi"},
    }


def test_update_without_change_writes_no_audit(admin) -> None:
    services.update_settings(admin, loan_period_days=14, library_name="Kütüphane")
    assert AuditEvent.objects.count() == 0


def test_only_changed_fields_are_audited(admin) -> None:
    services.update_settings(admin, loan_period_days=14, max_open_loans=5)
    assert AuditEvent.objects.get().details == {"max_open_loans": {"old": 3, "new": 5}}


def test_clerk_cannot_update_settings(clerk) -> None:
    with pytest.raises(PermissionDenied):
        services.update_settings(clerk, loan_period_days=21)
    assert services.get_settings().loan_period_days == 14
    assert AuditEvent.objects.count() == 0


def test_unknown_setting_is_a_programming_error(admin) -> None:
    with pytest.raises(TypeError):
        services.update_settings(admin, id=2)


@pytest.mark.parametrize(
    "field", ["loan_period_days", "max_open_loans", "debt_threshold_kurus", "retention_years"]
)
def test_tc19_zero_is_rejected_one_is_accepted(admin, field: str) -> None:
    before = getattr(services.get_settings(), field)
    with pytest.raises(RuleViolation):
        services.update_settings(admin, **{field: 0})
    assert getattr(services.get_settings(), field) == before
    assert AuditEvent.objects.count() == 0

    services.update_settings(admin, **{field: 1})
    assert getattr(services.get_settings(), field) == 1


@pytest.mark.parametrize("field", ["daily_fine_kurus", "fine_cap_kurus"])
def test_tc19_zero_fine_and_cap_are_accepted(admin, field: str) -> None:
    services.update_settings(admin, **{field: 0})
    assert getattr(services.get_settings(), field) == 0


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("loan_period_days", 366),
        ("max_open_loans", 21),
        ("retention_years", 11),
        ("daily_fine_kurus", -1),
        ("fine_cap_kurus", -1),
    ],
)
def test_settings_upper_and_negative_bounds_are_rejected(admin, field: str, value: int) -> None:
    with pytest.raises(RuleViolation):
        services.update_settings(admin, **{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [("loan_period_days", 365), ("max_open_loans", 20), ("retention_years", 10)],
)
def test_settings_upper_bounds_are_accepted(admin, field: str, value: int) -> None:
    services.update_settings(admin, **{field: value})
    assert getattr(services.get_settings(), field) == value


def test_tc20_library_name_length(admin) -> None:
    services.update_settings(admin, library_name="K" * 80)
    assert services.get_settings().library_name == "K" * 80
    for bad in ("K" * 81, ""):
        with pytest.raises(RuleViolation):
            services.update_settings(admin, library_name=bad)
    assert services.get_settings().library_name == "K" * 80


# --- Closed days (FR-24, ADR-0028, ADR-0040) ---------------------------------


def test_tc22_weekly_day_and_date_make_the_predicate(admin) -> None:
    services.set_weekly_closed(admin, {SUNDAY})
    added = services.add_closed_date(admin, date(2027, 10, 29), "Cumhuriyet Bayramı")
    is_closed = services.closed_day_predicate()
    assert is_closed(date(2027, 10, 31))  # Sunday
    assert is_closed(date(2027, 10, 29))
    assert not is_closed(date(2027, 11, 1))

    events = list(AuditEvent.objects.order_by("id"))
    assert [e.action for e in events] == [AuditAction.CLOSED_DAY_CHANGED] * 2
    assert (events[0].target_type, events[0].target_id) == ("weekly_closed_day", 0)
    assert events[0].details == {"op": "set", "old": [], "new": [SUNDAY]}
    assert (events[1].target_type, events[1].target_id) == ("closed_date", added.pk)
    assert events[1].details == {"op": "add", "date": "2027-10-29", "note": "Cumhuriyet Bayramı"}


def test_set_weekly_closed_replaces_rows(admin) -> None:
    services.set_weekly_closed(admin, {0, 1})
    services.set_weekly_closed(admin, {1, 2})
    assert set(WeeklyClosedDay.objects.values_list("weekday", flat=True)) == {1, 2}
    assert AuditEvent.objects.order_by("-id").first().details == {
        "op": "set",
        "old": [0, 1],
        "new": [1, 2],
    }


def test_set_weekly_closed_without_change_writes_no_audit(admin) -> None:
    services.set_weekly_closed(admin, set())
    assert AuditEvent.objects.count() == 0


def test_seven_weekly_days_are_rejected_by_the_service(admin) -> None:
    services.set_weekly_closed(admin, {0, 1, 2, 3, 4, 5})
    with pytest.raises(RuleViolation, match="En az bir gün açık kalmalı"):
        services.set_weekly_closed(admin, {0, 1, 2, 3, 4, 5, 6})
    assert WeeklyClosedDay.objects.count() == 6


def test_tc24_duplicate_closed_date_is_rejected(admin) -> None:
    services.add_closed_date(admin, date(2027, 10, 29))
    with pytest.raises(RuleViolation):
        services.add_closed_date(admin, date(2027, 10, 29))
    assert ClosedDate.objects.count() == 1
    assert AuditEvent.objects.count() == 1


def test_remove_closed_date_is_audited(admin) -> None:
    added = services.add_closed_date(admin, date(2027, 10, 29))
    services.remove_closed_date(admin, added.pk)
    assert ClosedDate.objects.count() == 0
    event = AuditEvent.objects.order_by("-id").first()
    assert (event.target_type, event.target_id) == ("closed_date", added.pk)
    assert event.details == {"op": "remove", "date": "2027-10-29"}


def test_remove_missing_closed_date_is_rejected(admin) -> None:
    with pytest.raises(RuleViolation):
        services.remove_closed_date(admin, 999)


@pytest.mark.parametrize(
    "call",
    [
        lambda actor: services.set_weekly_closed(actor, {SUNDAY}),
        lambda actor: services.add_closed_date(actor, date(2027, 10, 29)),
        lambda actor: services.remove_closed_date(actor, 1),
    ],
)
def test_clerk_cannot_change_closed_days(clerk, call) -> None:
    with pytest.raises(PermissionDenied):
        call(clerk)
    assert AuditEvent.objects.count() == 0


def test_tc246_closed_dates_holds_only_dates(admin) -> None:
    services.set_weekly_closed(admin, {SUNDAY})
    services.add_closed_date(admin, date(2027, 10, 29))
    services.add_closed_date(admin, date(2027, 10, 31))
    result = services.closed_dates()
    assert result == frozenset({date(2027, 10, 29), date(2027, 10, 31)})
    assert isinstance(result, frozenset)


def test_predicate_reads_the_database_once(admin) -> None:
    services.set_weekly_closed(admin, {SUNDAY})
    with CaptureQueriesContext(connection) as reads:
        is_closed = services.closed_day_predicate()
    selects = [q["sql"] for q in reads.captured_queries if q["sql"].startswith("SELECT")]
    assert len(selects) == 2  # weekly days and dates, once each
    with CaptureQueriesContext(connection) as later:
        assert [is_closed(date(2027, 11, d)) for d in range(1, 8)].count(True) == 1
    assert later.captured_queries == []


# --- TC-26: audit inside the service transaction (FR-26) ---------------------


def test_tc26_failure_after_audit_rolls_back_everything(admin, monkeypatch) -> None:
    real_record = services.record_audit

    def record_then_fail(*args, **kwargs):
        real_record(*args, **kwargs)
        raise RuntimeError("audit sonrasında hata")

    monkeypatch.setattr(services, "record_audit", record_then_fail)
    with pytest.raises(RuntimeError):
        services.add_closed_date(admin, date(2027, 10, 29))
    assert ClosedDate.objects.count() == 0
    assert AuditEvent.objects.count() == 0


# --- record_audit (phase 3 small decision 10) --------------------------------


def test_record_audit_writes_one_event(admin) -> None:
    event = record_audit(admin, AuditAction.STAFF_CHANGED, "staff_user", 5, {"change": "role"})
    assert event.pk is not None
    assert event.occurred_at is not None
    assert AuditEvent.objects.get().details == {"change": "role"}


def test_record_audit_allows_system_actor() -> None:
    event = record_audit(None, AuditAction.FEE, "ledger_entry", 1, {"amount_kurus": 100})
    assert event.actor is None


@pytest.mark.parametrize(
    "details",
    [
        {"member": 1, "loan": 2},
        {"member_no": 1, "loan_id": 2},
    ],
)
def test_record_audit_rejects_member_and_loan_together(admin, details) -> None:
    with pytest.raises(ValueError):
        record_audit(admin, AuditAction.FEE, "ledger_entry", 1, details)
    assert AuditEvent.objects.count() == 0


def test_audit_events_are_append_only(admin) -> None:
    event = record_audit(admin, AuditAction.FEE, "ledger_entry", 1, {})
    event.details = {"changed": True}
    with pytest.raises(ValueError):
        event.save()
    with pytest.raises(ValueError):
        event.delete()


# --- Job run log (KL-1, KL-33) ----------------------------------------------

T0 = datetime(2026, 11, 16, 2, 0, tzinfo=dt_timezone.utc)


def test_run_job_records_success(monkeypatch) -> None:
    clock = FrozenClock(monkeypatch, T0)

    def work(run_on: date) -> str:
        assert JobRun.objects.get().status == JobRun.Status.RUNNING
        clock.advance(minutes=5)
        return f"tamam {run_on.isoformat()}"

    run = jobs.run_job(jobs.Job.BACKUP, date(2026, 11, 16), work)
    run.refresh_from_db()
    assert run.status == JobRun.Status.SUCCESS
    assert run.detail == "tamam 2026-11-16"
    assert run.started_at == T0
    assert run.finished_at == T0 + timedelta(minutes=5)


def test_run_job_records_failure_and_reraises() -> None:
    def work(run_on: date) -> str:
        raise OSError("disk dolu")

    with pytest.raises(OSError):
        jobs.run_job(jobs.Job.BACKUP, date(2026, 11, 16), work)
    run = JobRun.objects.get()
    assert run.status == JobRun.Status.FAILED
    assert "disk dolu" in run.detail
    assert run.finished_at is not None


def _job(job, run_on, status, started, finished=None) -> JobRun:
    return JobRun.objects.create(
        job=job, run_on=run_on, status=status, started_at=started, finished_at=finished
    )


def test_last_success_and_last_finished() -> None:
    S, F, R = JobRun.Status.SUCCESS, JobRun.Status.FAILED, JobRun.Status.RUNNING
    assert jobs.last_success(jobs.Job.EXPORT) is None
    assert jobs.last_finished(jobs.Job.BACKUP) is None
    assert jobs.last_success_at(jobs.Job.BACKUP) is None

    _job(jobs.Job.BACKUP, date(2026, 11, 14), S, T0 - timedelta(days=2), T0 - timedelta(days=2))
    ok = _job(
        jobs.Job.BACKUP, date(2026, 11, 15), S, T0 - timedelta(days=1), T0 - timedelta(hours=23)
    )
    failed = _job(jobs.Job.BACKUP, date(2026, 11, 16), F, T0, T0 + timedelta(minutes=1))
    _job(jobs.Job.BACKUP, date(2026, 11, 16), R, T0 + timedelta(hours=1))
    _job(jobs.Job.EXPORT, date(2026, 11, 9), S, T0, T0)

    assert jobs.last_success(jobs.Job.BACKUP) == date(2026, 11, 15)
    assert jobs.last_success_at(jobs.Job.BACKUP) == ok.finished_at
    assert jobs.last_finished(jobs.Job.BACKUP) == failed
    assert jobs.last_success(jobs.Job.EXPORT) == date(2026, 11, 9)
    assert set(jobs.Job.values) == {"BACKUP", "ANONYMIZE", "REMINDERS", "EXPORT"}
