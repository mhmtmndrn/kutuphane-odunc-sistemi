"""Job run log for scheduled commands (KL-1, KL-33, NFR-05)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime

from django.utils import timezone

from .models import Job, JobRun

__all__ = ["Job", "run_job", "last_success", "last_finished", "last_success_at"]

_FINISHED = (JobRun.Status.SUCCESS, JobRun.Status.FAILED)


def run_job(job: Job, run_on: date, fn: Callable[[date], str]) -> JobRun:
    """Run ``fn(run_on)`` between a RUNNING row and its final status.

    The return value becomes ``detail``. An exception is recorded as FAILED
    with its text and re-raised.
    """
    run = JobRun.objects.create(
        job=job, run_on=run_on, started_at=timezone.now(), status=JobRun.Status.RUNNING
    )
    try:
        detail = fn(run_on)
    except Exception as exc:
        run.status = JobRun.Status.FAILED
        run.detail = f"{type(exc).__name__}: {exc}"
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "detail", "finished_at"])
        raise
    run.status = JobRun.Status.SUCCESS
    run.detail = detail
    run.finished_at = timezone.now()
    run.save(update_fields=["status", "detail", "finished_at"])
    return run


def last_success(job: Job) -> date | None:
    """``run_on`` of the latest successful run (used for catch-up and export age)."""
    run = (
        JobRun.objects.filter(job=job, status=JobRun.Status.SUCCESS)
        .order_by("-run_on", "-started_at")
        .first()
    )
    return run.run_on if run else None


def last_finished(job: Job) -> JobRun | None:
    """The latest SUCCESS or FAILED run by start time; RUNNING rows do not count."""
    return (
        JobRun.objects.filter(job=job, status__in=_FINISHED).order_by("-started_at", "-id").first()
    )


def last_success_at(job: Job) -> datetime | None:
    """``finished_at`` of the latest successful run (ADR-0044)."""
    run = (
        JobRun.objects.filter(job=job, status=JobRun.Status.SUCCESS)
        .order_by("-started_at", "-id")
        .first()
    )
    return run.finished_at if run else None
