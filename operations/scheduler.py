"""In-process scheduler and catch-up (G16; ADR-0007, ADR-0012, ADR-0053;
KL-5; G14–G16 small decisions 5 and 6).

``library_site/wsgi.py`` starts it only when ``LIBRARY_SCHEDULER_ENABLED`` is
"1"; tests and management commands do not load ``wsgi.py``. One worker runs
the jobs one after another, so the catch-up order holds and the export sees
the fresh backup. Every command runs through ``run_command``: a failure is
logged and never stops the scheduler.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from zoneinfo import ZoneInfo

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import close_old_connections
from django.utils import timezone

from administration.jobs import Job, last_success

from . import domain

logger = logging.getLogger("operations.scheduler")

TIME_ZONE = ZoneInfo("Europe/Istanbul")
# ADR-0053: queued work must not be dropped by the misfire check while the
# single worker is busy; piled-up firings collapse into one run.
JOB_OPTIONS = {"misfire_grace_time": 3600, "coalesce": True, "max_instances": 1}


@dataclass(frozen=True)
class ScheduledJob:
    job: Job
    command: str
    cron: dict


SCHEDULE: list[ScheduledJob] = [
    ScheduledJob(Job.BACKUP, "backup_db", {"hour": 2, "minute": 0}),
    ScheduledJob(Job.ANONYMIZE, "anonymize_expired", {"hour": 2, "minute": 30}),
    ScheduledJob(Job.REMINDERS, "send_reminders", {"hour": 9, "minute": 0}),
    ScheduledJob(Job.EXPORT, "export_backup", {"day_of_week": "mon", "hour": 3, "minute": 0}),
]
COMMANDS = {item.job: item.command for item in SCHEDULE}

# The running scheduler of this process, if any (read by tests).
_scheduler: BackgroundScheduler | None = None


def build_scheduler() -> BackgroundScheduler:
    """A scheduler with one worker thread (small decision 5)."""
    return BackgroundScheduler(
        timezone=TIME_ZONE,
        executors={"default": ThreadPoolExecutor(max_workers=1)},
        job_defaults=dict(JOB_OPTIONS),
    )


def run_command(command: str) -> None:
    """Run one management command; log the result and swallow every error
    (small decision 6). ``send_reminders`` raises ``CommandError`` when some
    e-mails failed while its ``job_run`` is SUCCESS (KL-23)."""
    close_old_connections()
    out = StringIO()
    try:
        call_command(command, stdout=out)
    except CommandError as exc:
        logger.error("Görev %s başarısız: %s", command, exc)
    except Exception:
        logger.exception("Görev %s beklenmeyen bir hatayla durdu", command)
    else:
        output = " / ".join(line for line in out.getvalue().splitlines() if line)
        logger.info("Görev %s tamamlandı: %s", command, output)
    finally:
        close_old_connections()


def catch_up(scheduler: BackgroundScheduler, now: datetime) -> list[Job]:
    """Queue the jobs whose latest planned run did not succeed (ADR-0007,
    ADR-0053). Ids carry the order, since jobs due at the same moment run in
    id order."""
    last = {job: last_success(job) for job in Job}
    due = domain.jobs_due_for_catch_up(now, last)
    for index, job in enumerate(due, start=1):
        command = COMMANDS[job]
        scheduler.add_job(
            run_command,
            DateTrigger(timezone=TIME_ZONE),
            args=[command],
            id=f"catch-up-{index}-{job.value.lower()}",
            name=f"Telafi: {job.value}",
            replace_existing=True,
            **JOB_OPTIONS,
        )
        logger.info("Telafi: %s kuyruğa alındı (%s)", job.value, command)
    return due


def run_catch_up(scheduler: BackgroundScheduler, now: datetime | None = None) -> None:
    """Start-up and hourly catch-up; an error is logged, not raised."""
    try:
        catch_up(scheduler, now or timezone.localtime(timezone=TIME_ZONE))
    except Exception:
        logger.exception("Telafi denetimi başarısız oldu")
    finally:
        close_old_connections()


def start_scheduler(now: datetime | None = None) -> BackgroundScheduler:
    """Start the four cron jobs and the hourly catch-up, log their next run
    times, then catch up once (``now`` is for tests)."""
    global _scheduler
    scheduler = build_scheduler()
    for item in SCHEDULE:
        scheduler.add_job(
            run_command,
            CronTrigger(timezone=TIME_ZONE, **item.cron),
            args=[item.command],
            id=item.job.value.lower(),
            name=item.command,
            **JOB_OPTIONS,
        )
    scheduler.add_job(
        run_catch_up,
        IntervalTrigger(hours=1, timezone=TIME_ZONE),
        args=[scheduler],
        id="catch-up",
        name="Saatlik telafi",
        **JOB_OPTIONS,
    )
    scheduler.start()
    for job in scheduler.get_jobs():
        logger.info("Zamanlanmış görev %s: sonraki çalışma %s", job.id, job.next_run_time)
    run_catch_up(scheduler, now)
    _scheduler = scheduler
    return scheduler
