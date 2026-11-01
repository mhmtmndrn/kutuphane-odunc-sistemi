"""Scheduler and catch-up (G16): TC-208…TC-213, TC-313, TC-314 and
TC-335…TC-339 (ADR-0007, ADR-0053; KL-4, KL-5; G14–G16 small decisions 5
and 6). TC-310…TC-312 are domain tests in ``test_domain.py``.

Tests that start a real scheduler patch ``call_command`` in the scheduler
module, so no command touches a database from the worker thread.
"""

from __future__ import annotations

import logging
import smtplib
import sys
import threading
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from django.core import mail
from django.core.mail.backends.locmem import EmailBackend
from django.core.management import call_command
from django.utils import timezone

from administration.models import Job, JobRun
from members.models import Member
from operations import domain, scheduler
from operations.tests.support import REPO_ROOT, lock_held_elsewhere
from tests.support.factories import make_loan, make_member

pytestmark = pytest.mark.django_db

ISTANBUL = ZoneInfo("Europe/Istanbul")
LOGGER = "operations.scheduler"


def at(day: int, hour: int, minute: int) -> datetime:
    return datetime(2026, 11, day, hour, minute, tzinfo=ISTANBUL)


def succeeded(job: Job, run_on: date, status: str = JobRun.Status.SUCCESS) -> JobRun:
    started = datetime.combine(run_on, datetime.min.time(), tzinfo=ISTANBUL) + timedelta(hours=2)
    return JobRun.objects.create(
        job=job,
        run_on=run_on,
        started_at=started,
        finished_at=started + timedelta(minutes=1),
        status=status,
        detail="",
    )


def all_done(day: date, *, except_: tuple[Job, ...] = ()) -> None:
    for job in Job:
        if job not in except_:
            succeeded(job, day)


def queued(sched) -> list[str]:
    return sorted(job.id for job in sched.get_jobs() if job.id.startswith("catch-up-"))


@pytest.fixture
def caplog(caplog: pytest.LogCaptureFixture):
    """The project loggers do not propagate (TC-339), so pytest's handler is
    attached to ``operations`` directly."""
    logger = logging.getLogger("operations")
    logger.addHandler(caplog.handler)
    yield caplog
    logger.removeHandler(caplog.handler)


@pytest.fixture
def stopped_scheduler():
    """A scheduler that is never started: added jobs stay pending."""
    return scheduler.build_scheduler()


@pytest.fixture
def started():
    """Collect started schedulers and shut them down after the test."""
    schedulers = []
    yield schedulers
    for sched in schedulers:
        if sched.running:
            sched.shutdown(wait=True)
    scheduler._scheduler = None


@pytest.fixture
def recorded(monkeypatch: pytest.MonkeyPatch):
    """Replace ``call_command`` in the scheduler; record calls and overlap."""
    calls: list[str] = []
    state = {"active": 0, "max_active": 0}
    done = threading.Event()
    lock = threading.Lock()

    def fake(command: str, *args, **kwargs) -> None:
        with lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        time.sleep(0.05)
        with lock:
            calls.append(command)
            state["active"] -= 1
        if len(calls) >= recorded_target[0]:
            done.set()

    recorded_target = [4]
    monkeypatch.setattr(scheduler, "call_command", fake)
    return calls, state, done, recorded_target


# --- TC-208, TC-335: the five triggers ---------------------------------------------


def test_tc208_tc335_schedule_and_job_options(started, recorded) -> None:
    all_done(timezone.localdate())  # nothing to catch up
    sched = scheduler.start_scheduler()
    started.append(sched)
    assert scheduler._scheduler is sched and sched.running
    jobs = {job.id: job for job in sched.get_jobs()}
    assert set(jobs) == {"backup", "anonymize", "reminders", "export", "catch-up"}

    expected = {
        "backup": ("backup_db", "2", "0", "*"),
        "anonymize": ("anonymize_expired", "2", "30", "*"),
        "reminders": ("send_reminders", "9", "0", "*"),
        "export": ("export_backup", "3", "0", "mon"),
    }
    for job_id, (command, hour, minute, day_of_week) in expected.items():
        job = jobs[job_id]
        assert isinstance(job.trigger, CronTrigger)
        fields = {field.name: str(field) for field in job.trigger.fields}
        assert (fields["hour"], fields["minute"], fields["day_of_week"]) == (
            hour,
            minute,
            day_of_week,
        )
        assert str(job.trigger.timezone) == "Europe/Istanbul"
        assert job.func is scheduler.run_command and job.args == (command,)

    hourly = jobs["catch-up"]
    assert isinstance(hourly.trigger, IntervalTrigger)
    assert hourly.trigger.interval == timedelta(hours=1)
    assert hourly.func is scheduler.run_catch_up

    for job in jobs.values():  # TC-335, ADR-0053
        assert (job.misfire_grace_time, job.coalesce, job.max_instances) == (3600, True, 1)
    executor = sched._lookup_executor("default")
    assert isinstance(executor, ThreadPoolExecutor)
    assert executor._pool._max_workers == 1


def test_schedule_matches_the_domain_times() -> None:
    by_job = {item.job: item for item in scheduler.SCHEDULE}
    assert [item.job for item in scheduler.SCHEDULE] == [
        Job.BACKUP,
        Job.ANONYMIZE,
        Job.REMINDERS,
        Job.EXPORT,
    ]
    for name, (weekday, planned) in domain.PLANNED.items():
        cron = by_job[Job(name)].cron
        assert (cron["hour"], cron["minute"]) == (planned.hour, planned.minute)
        assert cron.get("day_of_week") == (None if weekday is None else "mon")


def test_startup_logs_the_next_run_times(started, recorded, caplog) -> None:
    all_done(timezone.localdate())
    with caplog.at_level(logging.INFO, logger=LOGGER):
        started.append(scheduler.start_scheduler())
    lines = [r.getMessage() for r in caplog.records if r.name == LOGGER]
    for job_id in ("backup", "anonymize", "reminders", "export", "catch-up"):
        assert any(
            line.startswith(f"Zamanlanmış görev {job_id}: sonraki çalışma ") for line in lines
        )


# --- TC-209, TC-313: where the scheduler starts -------------------------------------

_IMPORT_WSGI = """
import library_site.wsgi
from operations import scheduler
print("scheduler:", scheduler._scheduler is not None, flush=True)
"""


def _wsgi(tmp_path: Path, **env: str):
    import os
    import subprocess

    full_env = {k: v for k, v in os.environ.items() if not k.startswith("LIBRARY_")}
    full_env.update(
        DJANGO_SETTINGS_MODULE="library_site.settings.test",
        LIBRARY_DB_PATH=str(tmp_path / "library.sqlite3"),
        PYTHONIOENCODING="utf-8",
        **env,
    )
    return subprocess.run(
        [sys.executable, "-c", _IMPORT_WSGI],
        cwd=REPO_ROOT,
        env=full_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )


@pytest.mark.parametrize("value", [None, "0"])
def test_tc209_scheduler_off_unless_enabled(tmp_path: Path, value: str | None) -> None:
    env = {} if value is None else {"LIBRARY_SCHEDULER_ENABLED": value}
    result = _wsgi(tmp_path, **env)
    assert result.returncode == 0, result.stderr
    assert "scheduler: False" in result.stdout


def test_tc209_management_commands_do_not_start_it() -> None:
    call_command("check", verbosity=0)
    assert scheduler._scheduler is None
    assert not [t for t in threading.enumerate() if "APScheduler" in t.name]


def test_wsgi_starts_the_scheduler_when_enabled(tmp_path: Path) -> None:
    # The child's database is not migrated: the start-up catch-up fails, is
    # logged, and the application still starts.
    result = _wsgi(tmp_path, LIBRARY_SCHEDULER_ENABLED="1")
    assert result.returncode == 0, result.stderr
    assert "scheduler: True" in result.stdout
    assert "Zamanlanmış görev catch-up: sonraki çalışma" in result.stderr
    assert "Telafi denetimi başarısız oldu" in result.stderr


def test_tc313_second_process_refused(tmp_path: Path) -> None:
    db = tmp_path / "library.sqlite3"
    with lock_held_elsewhere(db):
        result = _wsgi(tmp_path, LIBRARY_SCHEDULER_ENABLED="1")
    assert result.returncode != 0
    assert f"AppLockError: Uygulama zaten çalışıyor: {db}.app.lock" in result.stderr
    assert "scheduler:" not in result.stdout
    assert "Zamanlanmış görev" not in result.stderr


# --- TC-210…TC-212, TC-336: catch-up --------------------------------------------------


def test_tc210_reminders_before_and_after_nine(stopped_scheduler) -> None:
    day = date(2026, 11, 4)
    all_done(day, except_=(Job.REMINDERS,))
    succeeded(Job.REMINDERS, day - timedelta(days=1))
    assert scheduler.catch_up(stopped_scheduler, at(4, 8, 59)) == []
    assert queued(stopped_scheduler) == []
    assert scheduler.catch_up(stopped_scheduler, at(4, 9, 1)) == [Job.REMINDERS]
    assert queued(stopped_scheduler) == ["catch-up-1-reminders"]
    (job,) = [j for j in stopped_scheduler.get_jobs() if j.id == "catch-up-1-reminders"]
    assert isinstance(job.trigger, DateTrigger)
    assert job.func is scheduler.run_command and job.args == ("send_reminders",)
    assert (job.misfire_grace_time, job.coalesce, job.max_instances) == (3600, True, 1)


def test_tc211_success_today_or_failed_yesterday(stopped_scheduler) -> None:
    day = date(2026, 11, 4)
    all_done(day)
    assert scheduler.catch_up(stopped_scheduler, at(4, 10, 0)) == []

    JobRun.objects.filter(job=Job.REMINDERS).delete()
    succeeded(Job.REMINDERS, day - timedelta(days=2))
    succeeded(Job.REMINDERS, day - timedelta(days=1), JobRun.Status.FAILED)
    assert scheduler.catch_up(stopped_scheduler, at(4, 10, 0)) == [Job.REMINDERS]


def consenting(email: str) -> Member:
    member = make_member(email=email)
    Member.objects.filter(pk=member.pk).update(has_email_consent=True)
    return Member.objects.get(pk=member.pk)


def test_tc212_catch_up_once_per_day(stopped_scheduler, monkeypatch) -> None:
    day = date(2026, 11, 14)
    monkeypatch.setattr("administration.clock.today", lambda: day)
    make_loan(consenting("ayse@example.org"))  # due 2026-11-16: DUE_SOON on 11-14
    all_done(day, except_=(Job.REMINDERS,))
    assert scheduler.catch_up(stopped_scheduler, at(14, 10, 0)) == [Job.REMINDERS]
    for job in stopped_scheduler.get_jobs():
        job.func(*job.args)
        stopped_scheduler.remove_job(job.id)
    assert len(mail.outbox) == 1
    assert JobRun.objects.get(job=Job.REMINDERS).status == JobRun.Status.SUCCESS

    second_start = scheduler.build_scheduler()
    assert scheduler.catch_up(second_start, at(14, 10, 5)) == []
    assert len(mail.outbox) == 1


def test_tc336_hourly_catch_up_after_a_failed_backup(stopped_scheduler, caplog) -> None:
    day = date(2026, 11, 4)  # Wednesday
    succeeded(Job.BACKUP, day - timedelta(days=1))
    succeeded(Job.BACKUP, day, JobRun.Status.FAILED)
    succeeded(Job.ANONYMIZE, day)
    succeeded(Job.EXPORT, date(2026, 11, 2))
    succeeded(Job.REMINDERS, day - timedelta(days=1))  # 09:00 not reached yet
    with caplog.at_level(logging.INFO, logger=LOGGER):
        assert scheduler.catch_up(stopped_scheduler, at(4, 3, 10)) == [Job.BACKUP]
    assert queued(stopped_scheduler) == ["catch-up-1-backup"]
    assert "Telafi: BACKUP kuyruğa alındı (backup_db)" in caplog.messages

    succeeded(Job.BACKUP, day)
    later = scheduler.build_scheduler()
    assert scheduler.catch_up(later, at(4, 4, 10)) == []
    assert queued(later) == []


def test_hourly_job_uses_the_local_time(stopped_scheduler, monkeypatch) -> None:
    seen = []
    monkeypatch.setattr(scheduler, "catch_up", lambda sched, now: seen.append((sched, now)))
    scheduler.run_catch_up(stopped_scheduler)
    ((sched, now),) = seen
    assert sched is stopped_scheduler
    assert str(now.tzinfo) == "Europe/Istanbul"


def test_hourly_job_logs_its_own_errors(stopped_scheduler, monkeypatch, caplog) -> None:
    def broken(sched, now):
        raise RuntimeError("veritabanı kilitli")

    monkeypatch.setattr(scheduler, "catch_up", broken)
    with caplog.at_level(logging.INFO, logger=LOGGER):
        scheduler.run_catch_up(stopped_scheduler)  # does not raise
    (record,) = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert record.getMessage() == "Telafi denetimi başarısız oldu"
    assert record.exc_info is not None


# --- TC-337: one worker keeps the order -----------------------------------------------


def test_tc337_catch_up_runs_in_order_one_at_a_time(started, recorded) -> None:
    calls, state, done, _ = recorded
    sched = scheduler.start_scheduler(now=at(4, 10, 0))  # no job_run rows: all four due
    started.append(sched)
    assert done.wait(timeout=30), calls
    assert calls == ["backup_db", "anonymize_expired", "export_backup", "send_reminders"]
    assert state["max_active"] == 1


# --- TC-213, TC-338, TC-314: the command wrapper ----------------------------------------


def test_tc213_job_run_success(caplog) -> None:
    with caplog.at_level(logging.INFO, logger=LOGGER):
        scheduler.run_command("anonymize_expired")
    run = JobRun.objects.get()
    assert run.job == Job.ANONYMIZE and run.status == JobRun.Status.SUCCESS
    assert run.run_on == timezone.localdate() and run.finished_at is not None
    assert run.detail == "anonimleştirilen üye=0, bağı koparılan ödünç=0, ertelenen üye=0"
    assert (
        "Görev anonymize_expired tamamlandı: anonimleştirilen üye=0, bağı koparılan ödünç=0, "
        "ertelenen üye=0"
    ) in caplog.messages


def test_tc213_job_run_failed(monkeypatch, caplog) -> None:
    def broken(today):
        raise RuntimeError("disk dolu")

    monkeypatch.setattr("operations.services.anonymize_expired", broken)
    with caplog.at_level(logging.INFO, logger=LOGGER):
        scheduler.run_command("anonymize_expired")  # does not raise
    run = JobRun.objects.get()
    assert (run.status, run.detail) == (JobRun.Status.FAILED, "RuntimeError: disk dolu")
    assert run.finished_at is not None
    assert (
        "Görev anonymize_expired başarısız: Anonimleştirme yapılamadı: RuntimeError: disk dolu"
    ) in caplog.messages


def test_tc338_reminder_failure_is_logged(monkeypatch, caplog) -> None:
    def send_messages(self, messages):
        raise smtplib.SMTPServerDisconnected("Connection unexpectedly closed")

    monkeypatch.setattr(EmailBackend, "send_messages", send_messages)
    monkeypatch.setattr("administration.clock.today", lambda: date(2026, 11, 14))
    make_loan(consenting("ayse@example.org"))
    with caplog.at_level(logging.INFO, logger=LOGGER):
        scheduler.run_command("send_reminders")
    (record,) = [r for r in caplog.records if r.name == LOGGER and r.levelno == logging.ERROR]
    assert record.getMessage() == "Görev send_reminders başarısız: 1 hatırlatma gönderilemedi"
    assert JobRun.objects.get(job=Job.REMINDERS).status == JobRun.Status.SUCCESS


def test_tc338_unexpected_exception_is_logged(monkeypatch, caplog) -> None:
    def broken(command, *args, **kwargs):
        raise RuntimeError("beklenmeyen")

    monkeypatch.setattr(scheduler, "call_command", broken)
    with caplog.at_level(logging.INFO, logger=LOGGER):
        scheduler.run_command("backup_db")  # does not raise
    (record,) = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert record.name == LOGGER
    assert record.getMessage() == "Görev backup_db beklenmeyen bir hatayla durdu"
    assert record.exc_info[0] is RuntimeError


def test_tc314_failing_job_does_not_stop_the_scheduler(started, monkeypatch, caplog) -> None:
    ran = threading.Event()
    calls: list[str] = []

    def fake(command, *args, **kwargs):
        calls.append(command)
        if command == "first":
            raise RuntimeError("ilk görev bozuk")
        ran.set()

    monkeypatch.setattr(scheduler, "call_command", fake)
    sched = scheduler.build_scheduler()
    started.append(sched)
    with caplog.at_level(logging.INFO, logger=LOGGER):
        sched.start()
        sched.add_job(scheduler.run_command, DateTrigger(), args=["first"], id="a-first")
        sched.add_job(scheduler.run_command, DateTrigger(), args=["second"], id="b-second")
        assert ran.wait(timeout=30)
    assert calls == ["first", "second"]
    assert sched.running
    assert "Görev first beklenmeyen bir hatayla durdu" in caplog.messages


# --- TC-339: logging --------------------------------------------------------------------


def test_tc339_logging_to_stderr() -> None:
    config = settings.LOGGING
    handlers = config["handlers"]
    assert {h["class"] for h in handlers.values()} == {"logging.StreamHandler"}
    assert {h.get("stream") for h in handlers.values()} == {"ext://sys.stderr"}
    (formatter,) = config["formatters"].values()
    assert formatter["format"] == "%(asctime)s %(levelname)s %(name)s %(message)s"
    for name in ("operations", "django"):
        logger = config["loggers"][name]
        assert logger["level"] == "INFO"
        assert set(logger["handlers"]) <= set(handlers)
        assert logger["propagate"] is False  # no second line from a root handler
    assert logging.getLogger("operations.scheduler").getEffectiveLevel() == logging.INFO
