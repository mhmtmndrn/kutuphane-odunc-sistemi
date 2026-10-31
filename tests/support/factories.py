"""Plain test-data builders (phase 4 small decision 11; no factory_boy)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone as dt_timezone

from django.db.models import Max

from accounts.models import Role, StaffUser
from billing.models import EntryKind, LedgerEntry
from catalog.models import Book, Copy, CopyStatus
from circulation.models import CloseReason, Loan
from members.models import Member

# Ten characters or more and not a common password (KL-9).
DEFAULT_PASSWORD = "Kitap-Rafi-2026"


def make_staff(
    username: str = "ali",
    *,
    role: Role = Role.CLERK,
    password: str = DEFAULT_PASSWORD,
    full_name: str = "Ali Yılmaz",
    is_active: bool = True,
    must_change_password: bool = False,
) -> StaffUser:
    """Create a staff account. ``full_name`` is kept in ``first_name`` (plan §11, G02 (c))."""
    return StaffUser.objects.create_user(
        username=username,
        password=password,
        role=role,
        first_name=full_name,
        is_active=is_active,
        must_change_password=must_change_password,
    )


def make_member(
    full_name: str | None = "Ayşe Yılmaz",
    phone: str | None = "0555 111 22 33",
    email: str | None = None,
    *,
    member_no: int | None = None,
    is_active: bool = True,
    deactivated_on: date | None = None,
    anonymized: bool = False,
) -> Member:
    """Create a member directly (no actor, no audit).

    ``member_no`` defaults to the next free number. An inactive member gets
    ``deactivated_on`` 2026-10-01 unless given. ``anonymized=True`` builds
    the state that anonymization leaves (FR-25): inactive, personal fields
    NULL, ``anonymized_at`` set.
    """
    if member_no is None:
        member_no = (Member.objects.aggregate(top=Max("member_no"))["top"] or 0) + 1
    anonymized_at = None
    if anonymized:
        full_name = phone = email = None
        is_active = False
        anonymized_at = datetime(2026, 1, 1, tzinfo=dt_timezone.utc)
    if not is_active and deactivated_on is None:
        deactivated_on = date(2026, 10, 1)
    return Member.objects.create(
        member_no=member_no,
        full_name=full_name,
        phone=phone,
        email=email,
        is_active=is_active,
        deactivated_on=deactivated_on,
        anonymized_at=anonymized_at,
    )


def make_book(
    title: str = "Tutunamayanlar",
    author: str = "Oğuz Atay",
    *,
    isbn13: str | None = None,
    publisher: str | None = None,
    year: int | None = None,
) -> Book:
    """Create a book directly; ``isbn13`` is stored as given (no parsing)."""
    return Book.objects.create(
        title=title, author=author, isbn13=isbn13, publisher=publisher, year=year
    )


def make_copy(
    book: Book | None = None,
    *,
    pk: int | None = None,
    status: CopyStatus = CopyStatus.ON_SHELF,
) -> Copy:
    """Create a copy whose barcode is ``f"{id:08d}"``; ``pk`` fixes the id."""
    book = book or make_book()
    copy = Copy.objects.create(pk=pk, book=book, barcode="PENDING-", status=status)
    copy.barcode = f"{copy.pk:08d}"
    copy.save(update_fields=["barcode"])
    return copy


# The account that owns rows built by the factories below unless a test
# names one; a name no test uses for its own staff.
FACTORY_STAFF = "kayit.test"


def _factory_staff() -> StaffUser:
    staff = StaffUser.objects.filter(username=FACTORY_STAFF).first()
    return staff or make_staff(FACTORY_STAFF, full_name="Kayıt Testi")


_COPY_STATUS_AFTER = {
    None: CopyStatus.ON_LOAN,
    CloseReason.LOST: CopyStatus.LOST,
    CloseReason.DAMAGED: CopyStatus.DAMAGED,
}


def make_loan(
    member: Member | None = None,
    copy: Copy | None = None,
    *,
    loaned_on: date = date(2026, 11, 2),
    due_on: date | None = None,
    renewed_on: date | None = None,
    daily_fine_kurus: int = 500,
    fine_cap_kurus: int = 15000,
    closed_on: date | None = None,
    close_reason: CloseReason | None = None,
    copy_found_on: date | None = None,
    created_by: StaffUser | None = None,
) -> Loan:
    """Create a loan directly (no service, no audit).

    ``due_on`` defaults to ``loaned_on`` + 14 days. The copy's status follows
    the loan: ON_LOAN while open, LOST or DAMAGED after such a close; a
    RETURNED loan leaves it unchanged.
    """
    member = member if member is not None else make_member()
    copy = copy or make_copy()
    if close_reason is not None and closed_on is None:
        closed_on = due_on or loaned_on + timedelta(days=14)
    loan = Loan.objects.create(
        copy=copy,
        member=member,
        loaned_on=loaned_on,
        due_on=due_on or loaned_on + timedelta(days=14),
        renewed_on=renewed_on,
        daily_fine_kurus=daily_fine_kurus,
        fine_cap_kurus=fine_cap_kurus,
        closed_on=closed_on,
        close_reason=close_reason,
        closed_by=None if closed_on is None else (created_by or _factory_staff()),
        copy_found_on=copy_found_on,
        created_by=created_by or _factory_staff(),
    )
    status = _COPY_STATUS_AFTER.get(close_reason)
    if status is not None and copy.status != status:
        copy.status = status
        copy.save(update_fields=["status"])
    return loan


def make_charge(
    member: Member,
    kind: EntryKind = EntryKind.FINE,
    amount_kurus: int = 1500,
    *,
    loan: Loan | None = None,
    created_by: StaffUser | None = None,
    created_at: datetime | None = None,
) -> LedgerEntry:
    """Create a FINE or FEE directly (no allocation, no audit)."""
    if kind not in (EntryKind.FINE, EntryKind.FEE):
        raise ValueError("make_charge builds FINE and FEE entries only")
    return LedgerEntry.objects.create(
        member=member,
        loan=loan,
        kind=kind,
        amount_kurus=amount_kurus,
        created_by=created_by or _factory_staff(),
        created_at=created_at,
    )
