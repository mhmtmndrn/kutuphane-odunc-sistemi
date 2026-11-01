"""Seed data: ``operations.seed`` and ``load_seed_data`` (plan G17).

The real ``seed/books_openlibrary.json`` is not needed: tests point
``seed.BOOKS_FILE`` at a small sample or at a file they write (ADR-0056).
"""

from __future__ import annotations

import io
import json
import re
import socket
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest
from django.core.management import CommandError, call_command
from django.db import transaction
from django.db.models import F, Sum

from accounts.models import StaffUser
from administration import clock
from administration.models import AuditEvent, ClosedDate, LibrarySettings, WeeklyClosedDay
from billing.models import Allocation, EntryKind, LedgerEntry
from billing.services import member_balance, open_charges
from catalog.domain import copy_barcode, normalize_tr
from catalog.models import Book, Copy, CopyStatus
from circulation.domain import due_date, fine, late_days
from circulation.models import CloseReason, Loan
from members.domain import phone_digits
from members.models import ConsentAction, ConsentEvent, Member
from operations import seed
from tests.support.factories import make_book, make_member, make_staff

from .support import REPO_ROOT, manage

SAMPLE = Path(__file__).parent / "data" / "books_sample.json"
TODAY = date(2026, 11, 16)
FIRST_NAMES = set((REPO_ROOT / "seed" / "first_names.txt").read_text(encoding="utf-8").split())
LAST_NAMES = set((REPO_ROOT / "seed" / "last_names.txt").read_text(encoding="utf-8").split())
SAMPLE_TITLES = [b["title"] for b in json.loads(SAMPLE.read_text(encoding="utf-8"))["books"]]
SAMPLE_WORDS = set(re.findall(r"[^\W\d_]+", " ".join(SAMPLE_TITLES)))
TABLES = (Book, Copy, Member, ConsentEvent, Loan, LedgerEntry, Allocation)

pytestmark = pytest.mark.django_db


def isbn13(n: int) -> str:
    first12 = f"978605{n:06d}"
    total = sum(int(ch) * (3 if i % 2 else 1) for i, ch in enumerate(first12))
    return first12 + str((10 - total % 10) % 10)


def books_file(path: Path, n: int) -> Path:
    """A books file in the fetch script's format with ``n`` records."""
    books = [
        {"ol_id": f"OL{i}W", "title": f"Güz Kitabı {i}", "author": "Yazar Öztürk",
         "year": 2000, "isbn13": isbn13(i)}
        for i in range(1, n + 1)
    ]
    path.write_text(json.dumps({"_meta": {"count": n}, "books": books}), encoding="utf-8")
    return path


@pytest.fixture
def today(monkeypatch):
    monkeypatch.setattr(clock, "today", lambda: TODAY)
    return TODAY


@pytest.fixture
def sample(monkeypatch):
    monkeypatch.setattr(seed, "BOOKS_FILE", SAMPLE)
    return SAMPLE


@pytest.fixture
def actor(db):
    return make_staff("demo", full_name="Demo Personel")


def run(*args: str) -> list[str]:
    out = io.StringIO()
    call_command("load_seed_data", *args, stdout=out)
    return out.getvalue().splitlines()


@pytest.fixture
def demo(today, sample, actor):
    """TC-217's database: ``--profile demo --actor demo --seed 42``."""
    lines = run("--profile", "demo", "--actor", "demo", "--seed", "42")
    return lines


def snapshot() -> dict[str, list[tuple]]:
    return {
        model.__name__: [
            tuple(row) for row in model.objects.order_by("id").values_list()
        ]
        for model in TABLES
    }


class _Rollback(Exception):
    pass


def snapshot_of_run(day: date, monkeypatch, actor) -> dict[str, list[tuple]]:
    """Load, read every table, then roll back: a fresh empty database each time."""
    monkeypatch.setattr(clock, "today", lambda: day)
    result: dict = {}
    with pytest.raises(_Rollback):
        with transaction.atomic():
            seed.load("demo", 42, actor)
            result.update(snapshot())
            raise _Rollback
    assert not Book.objects.exists()
    return result


def assert_empty() -> None:
    for model in TABLES:
        assert not model.objects.exists(), model.__name__


# --- TC-217, TC-218, TC-219 ------------------------------------------------------


def test_tc217_demo_profile_counts(demo, today):
    assert Book.objects.count() == 300
    per_book = Counter(Copy.objects.values_list("book_id", flat=True))
    assert len(per_book) == 300 and set(per_book.values()) <= {1, 2, 3}
    assert Member.objects.count() == 200
    open_loans = Loan.objects.filter(closed_on__isnull=True)
    assert open_loans.count() == 150
    assert open_loans.filter(due_on__lt=today).count() == 10
    ol_books = Book.objects.filter(source_ol_id__isnull=False)
    assert sorted(ol_books.values_list("title", flat=True)) == sorted(SAMPLE_TITLES)
    assert all(re.fullmatch(r"OL\d+W", b.source_ol_id) for b in ol_books)
    for member in Member.objects.all():
        first, last = member.full_name.split(" ")
        assert first in FIRST_NAMES and last in LAST_NAMES


def test_tc218_same_seed_and_day_give_identical_data(monkeypatch, sample, actor):
    first = snapshot_of_run(TODAY, monkeypatch, actor)
    second = snapshot_of_run(TODAY, monkeypatch, actor)
    assert first == second
    assert len(first["Loan"]) == 500


def test_tc219_short_file_completed_synthetically_without_network(
    today, actor, tmp_path, monkeypatch
):
    monkeypatch.setattr(seed, "BOOKS_FILE", books_file(tmp_path / "books.json", 280))

    def no_network(*args, **kwargs):
        raise AssertionError("network access")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    lines = run("--actor", "demo")
    assert Book.objects.count() == 300
    assert Book.objects.filter(source_ol_id__isnull=True).count() == 20
    assert lines[1] == "Open Library dosyasında 280 kayıt var; 20 sentetik kitap eklendi"


# --- TC-315, TC-316 --------------------------------------------------------------


def test_tc315_missing_actor_is_usage_error(tmp_path):
    result = manage("load_seed_data", "--profile", "demo",
                    env={"LIBRARY_DB_PATH": str(tmp_path / "yok.sqlite3")})
    assert result.returncode == 2
    assert "--actor" in result.stderr


@pytest.mark.parametrize("name", ["yok", "eski"])
def test_tc315_unknown_or_inactive_actor(today, sample, name):
    make_staff("eski", is_active=False)
    with pytest.raises(CommandError, match=f"^Personel bulunamadı ya da pasif: {name}$"):
        run("--actor", name)
    assert_empty()


@pytest.mark.parametrize("existing", ["member", "book"])
def test_tc315_non_empty_database(today, sample, actor, existing):
    if existing == "member":
        make_member()
    else:
        make_book()
    before = snapshot()
    with pytest.raises(CommandError, match="^Veritabanı boş değil$"):
        run("--actor", "demo")
    assert snapshot() == before


def test_tc316_owner_status_consent_debt_and_email(demo, actor):
    staff = {actor.pk}
    assert set(Loan.objects.values_list("created_by", flat=True)) == staff
    assert set(Loan.objects.filter(closed_on__isnull=False).values_list("closed_by", flat=True)) == staff
    assert set(ConsentEvent.objects.values_list("recorded_by", flat=True)) == staff
    assert set(LedgerEntry.objects.values_list("created_by", flat=True)) == staff
    on_loan = set(Loan.objects.filter(closed_on__isnull=True).values_list("copy_id", flat=True))
    for copy in Copy.objects.all():
        assert copy.status == (CopyStatus.ON_LOAN if copy.pk in on_loan else CopyStatus.ON_SHELF)
    with_email = Member.objects.filter(email__isnull=False)
    assert with_email.count() == 100
    assert with_email.filter(has_email_consent=True).count() == 100
    assert sum(1 for m in Member.objects.all() if member_balance(m) > 0) == 5
    assert all(m.email.endswith("@example.invalid") for m in with_email)
    assert StaffUser.objects.count() == 1  # no staff account is created


# --- TC-341 … TC-352 -------------------------------------------------------------


def test_tc341_missing_books_file(today, actor, tmp_path, monkeypatch):
    missing = tmp_path / "yok" / "books_openlibrary.json"
    monkeypatch.setattr(seed, "BOOKS_FILE", missing)
    with pytest.raises(CommandError, match=f"^Kitap dosyası bulunamadı: {re.escape(str(missing))}$"):
        run("--actor", "demo")
    assert_empty()


def test_tc341_books_file_without_records(today, actor, tmp_path, monkeypatch):
    empty = books_file(tmp_path / "books.json", 0)
    monkeypatch.setattr(seed, "BOOKS_FILE", empty)
    with pytest.raises(CommandError, match=f"^Kitap dosyasında kayıt yok: {re.escape(str(empty))}$"):
        run("--actor", "demo")
    assert_empty()


def test_tc342_fake_phone_numbers(demo):
    phones = list(Member.objects.values_list("phone", "phone_digits"))
    assert len({phone for phone, _ in phones}) == 200
    for phone, digits in phones:
        assert re.fullmatch(r"000 \d{3} \d{2} \d{2}", phone)
        assert digits == phone_digits(phone) and len(digits) == 10 and digits.startswith("000")


def _dates_shifted(first, second) -> bool:
    for model, rows in first.items():
        for row1, row2 in zip(rows, second[model], strict=True):
            for v1, v2 in zip(row1, row2, strict=True):
                if isinstance(v1, (date, datetime)):
                    if v2 - v1 != timedelta(days=1):
                        return False
                elif v1 != v2:
                    return False
    return True


def test_tc343_dates_relative_to_today(today, sample, actor, monkeypatch):
    later = snapshot_of_run(today + timedelta(days=1), monkeypatch, actor)
    monkeypatch.setattr(clock, "today", lambda: today)
    seed.load("demo", 42, actor)
    closed = Loan.objects.filter(closed_on__isnull=False)
    assert closed.count() == 350
    window = today - timedelta(days=180)
    for loan in closed:
        assert window <= loan.loaned_on <= loan.closed_on <= today - timedelta(days=1)
    for loan in Loan.objects.filter(closed_on__isnull=True):
        assert loan.loaned_on <= today
    open_loans = Loan.objects.filter(closed_on__isnull=True)
    assert open_loans.filter(due_on__lt=today).count() == 10
    assert open_loans.filter(due_on__gte=today).count() == 140
    by_copy = defaultdict(list)
    for loan in Loan.objects.order_by("loaned_on"):
        by_copy[loan.copy_id].append(loan)
    for loans in by_copy.values():
        for earlier, later_loan in zip(loans, loans[1:]):
            assert earlier.closed_on is not None and earlier.closed_on < later_loan.loaned_on
    # The same seed one day later: every date moves by one day.
    assert _dates_shifted(snapshot(), later)


def test_tc344_debtors_owe_an_unpaid_late_fine(demo):
    debtors = [m for m in Member.objects.all() if member_balance(m) > 0]
    assert len(debtors) == 5
    for member in debtors:
        charges = open_charges(member)
        assert len(charges) == 1
        entry = LedgerEntry.objects.get(pk=charges[0].id)
        assert entry.kind == EntryKind.FINE and charges[0].unpaid == entry.amount_kurus
        assert entry.loan.close_reason == CloseReason.RETURNED
        assert entry.loan.closed_on > entry.loan.due_on
    fines = LedgerEntry.objects.filter(kind=EntryKind.FINE)
    assert fines.count() == 35
    payments = LedgerEntry.objects.filter(kind=EntryKind.PAYMENT)
    assert payments.count() == 30
    unpaid_ids = {open_charges(m)[0].id for m in debtors}
    for entry in fines.exclude(pk__in=unpaid_ids):
        assert payments.filter(member=entry.member, amount_kurus=entry.amount_kurus).exists()
    assert set(LedgerEntry.objects.values_list("kind", flat=True)) == {"FINE", "PAYMENT"}


def test_tc345_no_audit_and_consistent_allocations(demo):
    assert not AuditEvent.objects.exists()
    for payment in LedgerEntry.objects.filter(kind=EntryKind.PAYMENT):
        allocations = Allocation.objects.filter(credit_entry=payment)
        assert sum(a.amount_kurus for a in allocations) == payment.amount_kurus
        for allocation in allocations:
            assert allocation.charge_entry.kind == EntryKind.FINE
            assert allocation.charge_entry.member_id == payment.member_id
    for charge in LedgerEntry.objects.filter(kind=EntryKind.FINE):
        settled = charge.charge_allocations.aggregate(t=Sum("amount_kurus"))["t"] or 0
        assert settled <= charge.amount_kurus
    for member in Member.objects.all():
        assert member_balance(member) == sum(c.unpaid for c in open_charges(member))


def test_tc347_settings_and_domain_functions(today, sample, actor):
    LibrarySettings.objects.filter(pk=1).update(
        loan_period_days=21, daily_fine_kurus=200, fine_cap_kurus=3000
    )
    WeeklyClosedDay.objects.create(weekday=6)
    closed_day = today - timedelta(days=40)
    ClosedDate.objects.create(date=closed_day)
    run("--actor", "demo")
    closed = frozenset({closed_day})

    def is_closed(day: date) -> bool:
        return day.weekday() == 6 or day in closed

    for loan in Loan.objects.all():
        assert loan.due_on == due_date(loan.loaned_on, 21, is_closed)
        assert not is_closed(loan.due_on)
        assert (loan.daily_fine_kurus, loan.fine_cap_kurus) == (200, 3000)
    fines = LedgerEntry.objects.filter(kind=EntryKind.FINE).select_related("loan")
    assert fines.exists()
    for entry in fines:
        days = late_days(entry.loan.due_on, entry.loan.closed_on, closed)
        assert entry.amount_kurus == fine(days, 200, 3000) > 0
    assert copy_barcode(7) == "00000007"
    for copy in Copy.objects.all():
        assert copy.barcode == copy_barcode(copy.pk) == f"{copy.pk:08d}"
    for book in Book.objects.all():
        assert book.search_key == normalize_tr(f"{book.title} {book.author}")
    for member in Member.objects.all():
        assert member.search_key == normalize_tr(member.full_name)
        assert member.phone_digits == phone_digits(member.phone)


def test_tc348_failure_leaves_nothing(today, sample, actor, monkeypatch):
    original = seed._bulk

    def failing(model, rows):
        if model is Loan:
            raise RuntimeError("disk dolu")
        return original(model, rows)

    monkeypatch.setattr(seed, "_bulk", failing)
    with pytest.raises(CommandError, match="^Tohum verisi yüklenemedi: RuntimeError: disk dolu$"):
        run("--actor", "demo")
    assert_empty()


def test_tc349_synthetic_books(demo):
    synthetic = Book.objects.filter(source_ol_id__isnull=True)
    assert synthetic.count() == 288
    for book in synthetic:
        words = book.title.split(" ")
        assert 2 <= len(words) <= 4
        assert set(words) <= SAMPLE_WORDS
        first, last = book.author.split(" ")
        assert first in FIRST_NAMES and last in LAST_NAMES
        assert book.isbn13 is None and book.publisher is None


def test_tc350_output_lines(today, actor, tmp_path, monkeypatch):
    monkeypatch.setattr(seed, "BOOKS_FILE", books_file(tmp_path / "books.json", 300))
    lines = run("--actor", "demo")
    copies = Copy.objects.count()
    assert lines == [
        f"kitap=300, nüsha={copies}, üye=200, açık ödünç=150 (gecikmiş 10), kapalı ödünç=350"
    ]
    assert not Book.objects.filter(source_ol_id__isnull=True).exists()


def test_tc350_output_reports_synthetic_completion(demo):
    copies = Copy.objects.count()
    assert demo == [
        f"kitap=300, nüsha={copies}, üye=200, açık ödünç=150 (gecikmiş 10), kapalı ödünç=350",
        "Open Library dosyasında 12 kayıt var; 288 sentetik kitap eklendi",
    ]


def test_tc351_consent_events_and_email(demo, today, actor):
    for member in Member.objects.all():
        events = list(member.consent_events.all())
        if member.email is None:
            assert events == [] and not member.has_email_consent
            continue
        assert member.email == f"uye{member.member_no}@example.invalid"
        assert member.has_email_consent
        assert len(events) == 1 and events[0].action == ConsentAction.GIVEN
        assert today - timedelta(days=364) <= events[0].effective_on <= today
        assert events[0].recorded_by_id == actor.pk


def test_tc352_readme_sections():
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    sources = text.split("## Veri kaynakları", 1)[1].split("\n## ", 1)[0]
    assert "Open Library" in sources and "CC0" in sources
    demo_section = text.split("## Demo verisi", 1)[1].split("\n## ", 1)[0]
    steps = [
        demo_section.index("migrate"),
        demo_section.index("createsuperuser"),
        demo_section.index("load_seed_data --profile demo --actor <ad>"),
    ]
    assert steps == sorted(steps)


# --- Load profile (slow): TC-220, TC-317, TC-346 ----------------------------------


@pytest.fixture(scope="module")
def load_stats(django_db_setup, django_db_blocker):
    """Load ``--profile load`` once, collect the figures, roll back."""
    from operations.services import anonymize_expired

    stats: dict = {}
    with pytest.MonkeyPatch.context() as mp, django_db_blocker.unblock():
        mp.setattr(clock, "today", lambda: TODAY)
        mp.setattr(seed, "BOOKS_FILE", SAMPLE)
        with pytest.raises(_Rollback), transaction.atomic():
            actor = make_staff("demo")
            counts = seed.load("load", 42, actor)
            loans = Loan.objects.all()
            stats["counts"] = counts
            stats["books"] = Book.objects.count()
            stats["copies"] = Copy.objects.count()
            stats["members"] = Member.objects.count()
            stats["loans"] = loans.count()
            stats["open"] = loans.filter(closed_on__isnull=True).count()
            stats["overdue"] = loans.filter(closed_on__isnull=True, due_on__lt=TODAY).count()
            stats["email"] = Member.objects.filter(email__isnull=False).count()
            stats["consent"] = Member.objects.filter(has_email_consent=True).count()
            stats["closed"] = loans.filter(closed_on__isnull=False).count()
            stats["late_closed"] = loans.filter(closed_on__gt=F("due_on")).count()
            fines = list(LedgerEntry.objects.filter(kind=EntryKind.FINE).values_list(
                "member_id", "amount_kurus", "loan__closed_on", "loan__due_on"))
            payments = list(LedgerEntry.objects.filter(kind=EntryKind.PAYMENT).values_list(
                "member_id", "amount_kurus"))
            stats["fines"] = fines
            stats["payments"] = payments
            stats["kinds"] = set(LedgerEntry.objects.values_list("kind", flat=True))
            stats["min_loaned_on"] = min(loans.values_list("loaned_on", flat=True))
            stats["balances"] = {
                m.pk: member_balance(m)
                for m in Member.objects.filter(pk__in={f[0] for f in fines})
            }
            stats["anonymized"] = anonymize_expired(TODAY)
            raise _Rollback
    return stats


@pytest.mark.slow
def test_tc220_load_profile_counts(load_stats):
    assert load_stats["books"] == 15_000
    assert load_stats["copies"] == 20_000
    assert load_stats["members"] == 5_000
    assert load_stats["loans"] == 100_000
    assert load_stats["open"] == 3_000
    assert load_stats["overdue"] == 300
    assert load_stats["counts"].synthetic_books == 15_000 - 12


@pytest.mark.slow
def test_tc317_load_consent_and_paid_fines(load_stats):
    assert load_stats["email"] == load_stats["consent"] == 1_500
    assert load_stats["closed"] == 97_000
    assert len(load_stats["fines"]) == 9_700 == load_stats["late_closed"]
    assert all(closed_on > due_on for _, _, closed_on, due_on in load_stats["fines"])
    assert sorted(f[:2] for f in load_stats["fines"]) == sorted(load_stats["payments"])
    assert load_stats["kinds"] == {"FINE", "PAYMENT"}
    assert set(load_stats["balances"].values()) == {0}


@pytest.mark.slow
def test_tc346_load_within_365_days_and_untouched_by_retention(load_stats):
    assert load_stats["min_loaned_on"] >= TODAY - timedelta(days=365)
    anonymized = load_stats["anonymized"]
    assert (anonymized.members, anonymized.loans) == (0, 0)
