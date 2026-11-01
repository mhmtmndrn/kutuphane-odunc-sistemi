"""``backup_db [--date YYYY-MM-DD]`` (architecture §6.2, plan G14).

Runs inside ``run_job(Job.BACKUP, …)``; a failure is recorded as FAILED and
the command exits with 1.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from administration.jobs import Job, run_job
from operations import backup
from operations.cli import DATE_HELP, command_error, run_on_option


class Command(BaseCommand):
    help = "Veritabanının günlük yedeğini alır ve 30 günden eski yedekleri siler."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--date", help=DATE_HELP)

    def handle(self, *args, **options) -> None:
        run_on = run_on_option(options.get("date"))
        results: list[backup.BackupResult] = []

        def job(day) -> str:
            results.append(backup.backup_db(day))
            return f"{results[0].path.name}, silinen={len(results[0].deleted)}"

        try:
            run_job(Job.BACKUP, run_on, job)
        except Exception as exc:
            raise command_error(exc, "Yedek alınamadı") from exc
        self.stdout.write(f"Yedek alındı: {results[0].path}")
        self.stdout.write(f"Silinen eski yedek: {len(results[0].deleted)}")
