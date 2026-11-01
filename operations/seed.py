"""Seed data for demos and load tests (plan G17, FR-29, NFR-02).

``load(profile, seed, actor)`` writes books, copies, members, consent events,
loans and ledger rows into an empty database in one transaction with
``bulk_create`` (G17–G18 small decision 5). Everything is derived from
``random.Random(seed)`` and "today" (``administration.clock.today``), so the
same day and seed give the same rows (small decision 2). Rules come from the
existing domain functions and ``LibrarySettings``; no audit rows are written
(small decision 7).

Books come from ``seed/books_openlibrary.json`` (ADR-0033); missing books are
synthetic (small decision 6). The file is never fetched here (ADR-0056).
"""

from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Literal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from administration import clock
from administration.services import closed_dates, closed_day_predicate, get_settings
from billing.domain import OpenCharge, allocate_fifo
from billing.models import Allocation, EntryKind, LedgerEntry
from catalog.domain import copy_barcode, normalize_tr
from catalog.models import Book, Copy, CopyStatus
from circulation.domain import due_date, fine, late_days
from circulation.models import CloseReason, Loan
from members.domain import phone_digits
from members.models import ConsentAction, ConsentEvent, Member

SEED_DIR = Path(settings.BASE_DIR) / "seed"
BOOKS_FILE = SEED_DIR / "books_openlibrary.json"
FIRST_NAMES_FILE = SEED_DIR / "first_names.txt"
LAST_NAMES_FILE = SEED_DIR / "last_names.txt"

EMAIL_DOMAIN = "example.invalid"
MAX_OL_BOOKS = 300  # ADR-0033
MAX_LATE_DAYS = 20  # days after the due date of a late return or an overdue loan
SHIFT_ROOM_DAYS = 7  # room left in a slot for the closed-day shift
CONSENT_WINDOW_DAYS = 365  # small decision 9
SYNTHETIC_YEAR_FROM = 1950
BATCH_SIZE = 2000
_WORD = re.compile(r"[^\W\d_]+")


class SeedError(Exception):
    """An expected refusal; the message is shown to the operator as is."""


@dataclass(frozen=True)
class Profile:
    books: int
    copies: int | None  # None: 1–3 copies per book
    members: int
    consent_share: float
    open_loans: int
    overdue: int
    closed_loans: int
    window_days: int  # closed loans fall within the last ``window_days`` days
    late_share: float
    debtors: int


# KL-16, phase 4 small decision 12, G17–G18 small decisions 3 and 4.
PROFILES = {
    "demo": Profile(
        books=300, copies=None, members=200, consent_share=0.5, open_loans=150, overdue=10,
        closed_loans=350, window_days=180, late_share=0.1, debtors=5,
    ),
    "load": Profile(
        books=15_000, copies=20_000, members=5_000, consent_share=0.3, open_loans=3_000,
        overdue=300, closed_loans=97_000, window_days=365, late_share=0.1, debtors=0,
    ),
}


@dataclass(frozen=True)
class SeedCounts:
    books: int
    copies: int
    members: int
    open_loans: int
    overdue_loans: int
    closed_loans: int
    ol_records: int  # records in the books file
    synthetic_books: int


def counts_lines(counts: SeedCounts) -> list[str]:
    """The command output (small decision 8)."""
    lines = [
        f"kitap={counts.books}, nüsha={counts.copies}, üye={counts.members}, "
        f"açık ödünç={counts.open_loans} (gecikmiş {counts.overdue_loans}), "
        f"kapalı ödünç={counts.closed_loans}"
    ]
    if counts.synthetic_books:
        lines.append(
            f"Open Library dosyasında {counts.ol_records} kayıt var; "
            f"{counts.synthetic_books} sentetik kitap eklendi"
        )
    return lines


def seed_phone(number: int) -> str:
    """ADR-0057: "000" and seven digits, as ``000 ddd dd dd``."""
    digits = f"{number:07d}"
    return f"000 {digits[:3]} {digits[3:5]} {digits[5:]}"


def seed_email(member_no: int) -> str:
    return f"uye{member_no}@{EMAIL_DOMAIN}"


def title_words(titles: list[str]) -> list[str]:
    """Distinct letter-only words of the titles, in first-seen order."""
    return list(dict.fromkeys(word for title in titles for word in _WORD.findall(title)))


def read_books(path: Path) -> list[dict]:
    if not path.is_file():
        raise SeedError(f"Kitap dosyası bulunamadı: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data["books"])


def _names(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _at(day: date, hour: int, minute: int = 0) -> datetime:
    return timezone.make_aware(datetime.combine(day, time(hour, minute)))


def _bulk(model, rows: list) -> None:
    """The single write path; tests inject a failure here (TC-348)."""
    model.objects.bulk_create(rows, batch_size=BATCH_SIZE)


@dataclass
class _LoanRow:
    copy_id: int
    member_id: int
    loaned_on: date
    due_on: date
    closed_on: date | None = None


def load(profile: Literal["demo", "load"], seed: int, actor) -> SeedCounts:
    spec = PROFILES[profile]
    with transaction.atomic():
        if Member.objects.exists() or Book.objects.exists():
            raise SeedError("Veritabanı boş değil")
        return _Builder(spec, seed, actor).write()


class _Builder:
    def __init__(self, spec: Profile, seed: int, actor) -> None:
        self.spec = spec
        self.rng = random.Random(seed)
        self.actor = actor
        self.today = clock.today()
        library = get_settings()
        self.period = library.loan_period_days
        self.daily_fine = library.daily_fine_kurus
        self.fine_cap = library.fine_cap_kurus
        self.is_closed = closed_day_predicate()
        self.closed = closed_dates()
        self.records = read_books(BOOKS_FILE)
        self.first_names = _names(FIRST_NAMES_FILE)
        self.last_names = _names(LAST_NAMES_FILE)

    def _person(self) -> str:
        return f"{self.rng.choice(self.first_names)} {self.rng.choice(self.last_names)}"

    def _due(self, loaned_on: date) -> date:
        return due_date(loaned_on, self.period, self.is_closed)

    # --- Books and copies --------------------------------------------------------

    def _books(self) -> tuple[list[Book], int]:
        ol = self.records[: min(MAX_OL_BOOKS, self.spec.books)]
        synthetic = self.spec.books - len(ol)
        words = title_words([str(record["title"]) for record in self.records])
        if synthetic and not words:
            raise SeedError(f"Kitap dosyasında kayıt yok: {BOOKS_FILE}")
        books = []
        for record in ol:
            books.append(
                {
                    "title": record["title"],
                    "author": record["author"],
                    "year": record.get("year"),
                    "isbn13": record.get("isbn13"),
                    "source_ol_id": record.get("ol_id"),
                }
            )
        for _ in range(synthetic):
            title = " ".join(self.rng.choice(words) for _ in range(self.rng.randint(2, 4)))
            books.append(
                {
                    "title": title,
                    "author": self._person(),
                    "year": self.rng.randint(SYNTHETIC_YEAR_FROM, self.today.year),
                    "isbn13": None,
                    "source_ol_id": None,
                }
            )
        rows = [
            Book(id=pk, search_key=normalize_tr(f"{b['title']} {b['author']}"), publisher=None, **b)
            for pk, b in enumerate(books, start=1)
        ]
        return rows, synthetic

    def _copy_book_ids(self) -> list[int]:
        """The book of each copy, in copy id order."""
        n = self.spec.books
        if self.spec.copies is None:
            per_book = [self.rng.randint(1, 3) for _ in range(n)]
        else:
            second = set(self.rng.sample(range(n), self.spec.copies - n))
            per_book = [2 if i in second else 1 for i in range(n)]
        return [book_id for book_id, k in enumerate(per_book, start=1) for _ in range(k)]

    # --- Members and consent -----------------------------------------------------

    def _members(self) -> tuple[list[Member], list[ConsentEvent]]:
        n = self.spec.members
        phones = self.rng.sample(range(10**7), n)
        consenting = set(self.rng.sample(range(n), round(n * self.spec.consent_share)))
        members, events = [], []
        for index in range(n):
            member_no = index + 1
            full_name = self._person()
            phone = seed_phone(phones[index])
            given = index in consenting
            members.append(
                Member(
                    id=member_no,
                    member_no=member_no,
                    full_name=full_name,
                    phone=phone,
                    phone_digits=phone_digits(phone),
                    email=seed_email(member_no) if given else None,
                    search_key=normalize_tr(full_name),
                    has_email_consent=given,
                )
            )
            if given:
                effective_on = self.today - timedelta(
                    days=self.rng.randint(0, CONSENT_WINDOW_DAYS - 1)
                )
                events.append(
                    ConsentEvent(
                        member_id=member_no,
                        action=ConsentAction.GIVEN,
                        effective_on=effective_on,
                        recorded_at=_at(effective_on, 10),
                        recorded_by=self.actor,
                    )
                )
        for pk, event in enumerate(events, start=1):
            event.id = pk
        return members, events

    # --- Loans -------------------------------------------------------------------

    def _open_loans(self, copy_ids: list[int], member_ids: list[int]) -> list[_LoanRow]:
        spec = self.spec
        order = list(member_ids)
        self.rng.shuffle(order)
        rows = []
        for j, copy_id in enumerate(self.rng.sample(copy_ids, spec.open_loans)):
            if j < spec.overdue:
                loaned_on = self.today - timedelta(
                    days=self.period + self.rng.randint(1, MAX_LATE_DAYS)
                )
                due_on = self._due(loaned_on)
                while due_on >= self.today:
                    loaned_on -= timedelta(days=1)
                    due_on = self._due(loaned_on)
            else:
                loaned_on = self.today - timedelta(days=self.rng.randint(0, self.period - 1))
                due_on = self._due(loaned_on)
            rows.append(_LoanRow(copy_id, order[j % len(order)], loaned_on, due_on))
        return rows

    def _closed_loan(self, start: date, end: date, late: bool) -> tuple[date, date, date]:
        """A loan inside ``[start, end]``; late returns come back after the due date."""
        span = (end - start).days
        if late:
            extra = self.rng.randint(1, MAX_LATE_DAYS)
            room = span - self.period - extra - SHIFT_ROOM_DAYS
            loaned_on = start + timedelta(days=self.rng.randint(0, max(0, room)))
            due_on = self._due(loaned_on)
            closed_on = min(due_on + timedelta(days=extra), end)
        else:
            room = span - self.period
            loaned_on = start + timedelta(days=self.rng.randint(0, max(0, room)))
            due_on = self._due(loaned_on)
            closed_on = min(loaned_on + timedelta(days=self.rng.randint(1, self.period)), end)
        return loaned_on, due_on, closed_on

    def _closed_loans(
        self, copy_ids: list[int], member_ids: list[int], open_from: dict[int, date]
    ) -> list[_LoanRow]:
        """Closed loans; each copy's loans sit in their own slots and never overlap
        its open loan."""
        spec = self.spec
        order = list(copy_ids)
        self.rng.shuffle(order)
        per_copy: dict[int, list[int]] = defaultdict(list)
        for k in range(spec.closed_loans):
            per_copy[order[k % len(order)]].append(k)
        late = set(self.rng.sample(range(spec.closed_loans), round(spec.closed_loans * spec.late_share)))
        window_start = self.today - timedelta(days=spec.window_days)
        rows = []
        for copy_id in sorted(per_copy):
            ks = per_copy[copy_id]
            end = open_from.get(copy_id, self.today) - timedelta(days=1)
            slot = ((end - window_start).days + 1) // len(ks)
            for s, k in enumerate(ks):
                a = window_start + timedelta(days=s * slot)
                b = end if s == len(ks) - 1 else a + timedelta(days=slot - 1)
                loaned_on, due_on, closed_on = self._closed_loan(a, b, k in late)
                rows.append(
                    _LoanRow(copy_id, self.rng.choice(member_ids), loaned_on, due_on, closed_on)
                )
        return rows

    # --- Ledger ------------------------------------------------------------------

    def _ledger(self, loans: list[Loan]) -> tuple[list[LedgerEntry], list[Allocation]]:
        """A FINE for every late return; a PAYMENT of the same amount unless the
        member is one of the debtors (small decision 3). Allocations are FIFO."""
        fined = []
        for loan in loans:
            if loan.closed_on is None:
                continue
            amount = fine(
                late_days(loan.due_on, loan.closed_on, self.closed),
                loan.daily_fine_kurus,
                loan.fine_cap_kurus,
            )
            if amount > 0:
                fined.append((loan, amount))
        unpaid: set[int] = set()
        if self.spec.debtors:
            latest: dict[int, Loan] = {}
            for loan, _ in fined:
                current = latest.get(loan.member_id)
                if current is None or (loan.closed_on, loan.id) > (current.closed_on, current.id):
                    latest[loan.member_id] = loan
            candidates = sorted(latest)
            for member_id in self.rng.sample(candidates, min(self.spec.debtors, len(candidates))):
                unpaid.add(latest[member_id].id)

        events = []
        for loan, amount in fined:
            events.append((_at(loan.closed_on, 12), loan.id, 0, loan, amount))
            if loan.id not in unpaid:
                events.append((_at(loan.closed_on, 12, 5), loan.id, 1, loan, amount))
        events.sort(key=lambda event: event[:3])
        entries, allocations = [], []
        open_by_member: dict[int, list[OpenCharge]] = defaultdict(list)
        for pk, (created_at, _, is_payment, loan, amount) in enumerate(events, start=1):
            kind = EntryKind.PAYMENT if is_payment else EntryKind.FINE
            entries.append(
                LedgerEntry(
                    id=pk,
                    member_id=loan.member_id,
                    loan_id=None if is_payment else loan.id,
                    kind=kind,
                    amount_kurus=amount,
                    created_at=created_at,
                    created_by=self.actor,
                )
            )
            charges = open_by_member[loan.member_id]
            if not is_payment:
                charges.append(OpenCharge(pk, amount))
                continue
            remaining = {charge.id: charge.unpaid for charge in charges}
            for charge_id, part in allocate_fifo(charges, amount):
                allocations.append(
                    Allocation(
                        id=len(allocations) + 1,
                        credit_entry_id=pk,
                        charge_entry_id=charge_id,
                        amount_kurus=part,
                    )
                )
                remaining[charge_id] -= part
            open_by_member[loan.member_id] = [
                OpenCharge(charge.id, remaining[charge.id])
                for charge in charges
                if remaining[charge.id] > 0
            ]
        return entries, allocations

    # --- Writing -----------------------------------------------------------------

    def write(self) -> SeedCounts:
        books, synthetic = self._books()
        copy_books = self._copy_book_ids()
        copy_ids = list(range(1, len(copy_books) + 1))
        members, events = self._members()
        member_ids = [member.id for member in members]

        open_rows = self._open_loans(copy_ids, member_ids)
        open_from = {row.copy_id: row.loaned_on for row in open_rows}
        closed_rows = self._closed_loans(copy_ids, member_ids, open_from)
        rows = sorted(open_rows + closed_rows, key=lambda r: (r.loaned_on, r.copy_id))
        loans = [
            Loan(
                id=pk,
                copy_id=row.copy_id,
                member_id=row.member_id,
                loaned_on=row.loaned_on,
                due_on=row.due_on,
                daily_fine_kurus=self.daily_fine,
                fine_cap_kurus=self.fine_cap,
                closed_on=row.closed_on,
                close_reason=CloseReason.RETURNED if row.closed_on else None,
                created_by=self.actor,
                closed_by=self.actor if row.closed_on else None,
            )
            for pk, row in enumerate(rows, start=1)
        ]
        entries, allocations = self._ledger(loans)

        # Loans are in ``loaned_on`` order and never overlap on a copy, so the
        # last one seen is the copy's latest status change.
        last_change: dict[int, datetime] = {}
        for loan in loans:
            moment = _at(loan.loaned_on, 10) if loan.closed_on is None else _at(loan.closed_on, 12)
            last_change[loan.copy_id] = moment
        acquired = _at(self.today - timedelta(days=self.spec.window_days), 9)
        copies = [
            Copy(
                id=copy_id,
                book_id=book_id,
                barcode=copy_barcode(copy_id),
                status=CopyStatus.ON_LOAN if copy_id in open_from else CopyStatus.ON_SHELF,
                status_changed_at=last_change.get(copy_id, acquired),
            )
            for copy_id, book_id in zip(copy_ids, copy_books, strict=True)
        ]

        for model, batch in (
            (Book, books),
            (Copy, copies),
            (Member, members),
            (ConsentEvent, events),
            (Loan, loans),
            (LedgerEntry, entries),
            (Allocation, allocations),
        ):
            _bulk(model, batch)
        return SeedCounts(
            books=len(books),
            copies=len(copies),
            members=len(members),
            open_loans=len(open_rows),
            overdue_loans=sum(1 for row in open_rows if row.due_on < self.today),
            closed_loans=len(closed_rows),
            ol_records=len(self.records),
            synthetic_books=synthetic,
        )
