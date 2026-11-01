"""``export_backup [--date YYYY-MM-DD] [--passphrase-file PATH]``
(architecture §6.2, plan G14, ADR-0006, ADR-0011).

Encrypts the newest daily backup; the passphrase file defaults to
``LIBRARY_EXPORT_PASSPHRASE_FILE``. Runs inside ``run_job(Job.EXPORT, …)``.
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from administration.jobs import Job, run_job
from operations import backup
from operations.cli import DATE_HELP, command_error, run_on_option


class Command(BaseCommand):
    help = "Son günlük yedeği parolayla şifreleyip bina dışı yedek dosyası (.libx) üretir."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--date", help=DATE_HELP)
        parser.add_argument(
            "--passphrase-file", help="Parola dosyası; varsayılan LIBRARY_EXPORT_PASSPHRASE_FILE"
        )

    def handle(self, *args, **options) -> None:
        run_on = run_on_option(options.get("date"))
        passphrase_file = Path(
            options.get("passphrase_file") or settings.LIBRARY_EXPORT_PASSPHRASE_FILE
        )
        results: list[backup.ExportResult] = []

        def job(day) -> str:
            results.append(backup.export_backup(day, passphrase_file))
            result = results[0]
            return f"{result.path.name} (kaynak {result.source}), silinen={len(result.deleted)}"

        try:
            run_job(Job.EXPORT, run_on, job)
        except Exception as exc:
            raise command_error(exc, "Dışa aktarma yapılamadı") from exc
        result = results[0]
        self.stdout.write(f"Dışa aktarıldı: {result.path} (kaynak: {result.source})")
        self.stdout.write(f"Silinen eski dışa aktarma: {len(result.deleted)}")
