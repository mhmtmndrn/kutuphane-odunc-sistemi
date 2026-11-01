"""``anonymize_expired [--date YYYY-MM-DD]`` (architecture §6.2, plan G15).

Runs inside ``run_job(Job.ANONYMIZE, …)``. The first error stops the run:
earlier records stay processed, ``job_run`` is FAILED and the exit code is 1
(G14–G16 small decision 9).
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from administration.jobs import Job, run_job
from operations import domain, services
from operations.cli import DATE_HELP, command_error, run_on_option


class Command(BaseCommand):
    help = (
        "Saklama süresi dolan ödünçlerin üye bağını koparır ve süresi dolan pasif üyeleri "
        "anonimleştirir; borçlu üyeler ertelenir."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument("--date", help=DATE_HELP)

    def handle(self, *args, **options) -> None:
        run_on = run_on_option(options.get("date"))

        def job(day) -> str:
            return domain.anonymize_counts_text(services.anonymize_expired(day))

        try:
            run = run_job(Job.ANONYMIZE, run_on, job)
        except Exception as exc:
            raise command_error(exc, "Anonimleştirme yapılamadı") from exc
        self.stdout.write(run.detail)
