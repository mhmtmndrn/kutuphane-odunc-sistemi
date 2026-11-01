"""``restore_backup PATH [--passphrase-file PATH] --yes`` (architecture §6.2,
plan G14, ADR-0054, KL-41).

The application must be stopped (KL-4). The current database is kept as
``<db>.pre-restore-YYYYMMDD-HHMMSS``; no migrations are run. Exit codes: 0
success, 1 error, 2 usage error (missing PATH or ``--yes``).
"""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand

from operations import backup
from operations.cli import command_error


class Command(BaseCommand):
    help = (
        "Veritabanını bir günlük yedekten (.sqlite3) ya da şifreli dışa aktarmadan (.libx) "
        "geri yükler. Uygulama durdurulmuş olmalıdır."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument("path", help="Geri yüklenecek yedek ya da dışa aktarma dosyası")
        parser.add_argument(
            "--passphrase-file",
            help="Şifreli dosyanın parola dosyası; varsayılan LIBRARY_EXPORT_PASSPHRASE_FILE",
        )
        parser.add_argument(
            "--yes",
            action="store_true",
            required=True,
            help="Veritabanının değiştirileceğini onaylar",
        )

    def handle(self, *args, **options) -> None:
        passphrase_file = options.get("passphrase_file")
        try:
            result = backup.restore(
                Path(options["path"]), Path(passphrase_file) if passphrase_file else None
            )
        except Exception as exc:
            raise command_error(exc, "Geri yükleme yapılamadı") from exc
        counts = result.counts
        self.stdout.write(
            f"Geri yüklendi: üye={counts.members}, nüsha={counts.copies}, ödünç={counts.loans}"
        )
        if result.pre_restore is not None:
            self.stdout.write(f"Önceki veritabanı korundu: {result.pre_restore}")
        self.stdout.write("Gerekirse python manage.py migrate çalıştırın.")
