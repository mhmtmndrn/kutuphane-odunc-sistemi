"""``load_seed_data --profile demo|load --actor <ad> [--seed 42]`` (plan G17).

Loads demo or load-test data into an empty database (ADR-0038, KL-16). The
command never goes to the network (ADR-0033, ADR-0056) and writes no
``job_run`` or audit rows.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from accounts.models import StaffUser
from operations import seed


class Command(BaseCommand):
    help = (
        "Boş veritabanına demo ya da yük testi verisi yükler; kayıtların sahibi "
        "--actor personelidir."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--profile",
            choices=sorted(seed.PROFILES),
            default="demo",
            help="demo ya da load; varsayılan demo",
        )
        parser.add_argument(
            "--actor",
            required=True,
            help="Kayıtların sahibi olacak aktif personelin kullanıcı adı",
        )
        parser.add_argument(
            "--seed", type=int, default=42, help="Rastgele üretecin tohumu; varsayılan 42"
        )

    def handle(self, *args, **options) -> None:
        name = options["actor"]
        actor = StaffUser.objects.filter(username=name, is_active=True).first()
        if actor is None:
            raise CommandError(f"Personel bulunamadı ya da pasif: {name}")
        try:
            counts = seed.load(options["profile"], options["seed"], actor)
        except seed.SeedError as exc:
            raise CommandError(str(exc)) from exc
        except Exception as exc:
            raise CommandError(
                f"Tohum verisi yüklenemedi: {type(exc).__name__}: {exc}"
            ) from exc
        for line in seed.counts_lines(counts):
            self.stdout.write(line)
