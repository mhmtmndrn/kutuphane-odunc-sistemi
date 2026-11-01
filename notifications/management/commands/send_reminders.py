"""``send_reminders [--date YYYY-MM-DD]`` (architecture §6.2, plan G13).

Runs inside ``run_job(Job.REMINDERS, …)``. The ``job_run`` row is SUCCESS
even when some e-mails failed; its detail and the output carry the counts,
and the exit code is 1 when at least one reminder failed (KL-23).
"""

from __future__ import annotations

from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError

from administration import clock
from administration.jobs import Job, run_job
from notifications import domain, services


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise CommandError(f"Geçersiz tarih: {value}") from None


class Command(BaseCommand):
    help = "Son tarihi yaklaşan ve geciken ödünçler için hatırlatma e-postalarını gönderir."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--date", help="YYYY-MM-DD; varsayılan bugün")

    def handle(self, *args, **options) -> None:
        value = options.get("date")
        run_on = _parse_date(value) if value else clock.today()
        result: list[domain.ReminderCounts] = []

        def job(day: date) -> str:
            result.append(services.send_due_reminders(day))
            return domain.counts_text(result[0])

        run = run_job(Job.REMINDERS, run_on, job)
        self.stdout.write(run.detail)
        if result[0].failed:
            raise CommandError(f"{result[0].failed} hatırlatma gönderilemedi", returncode=1)
