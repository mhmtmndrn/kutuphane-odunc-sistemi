"""Book and copy services (plan G07). Each public function is one transaction.

Creating or updating books and adding copies writes no audit event; the
audit actions of phase 4 small decision 8 do not include them.
"""

from __future__ import annotations

import functools
import operator

from django.db import transaction
from django.db.models import Case, Count, IntegerField, Q, Value, When

from accounts.models import Role
from accounts.permissions import require_role
from administration.errors import RuleViolation
from administration.services import get_settings
from pdf.sheets import LABEL_LAYOUT, SheetItem, render_sheet

from .domain import IsbnOk, IsbnSuggest, normalize_tr, parse_isbn
from .models import Book, Copy, CopyStatus

SEARCH_LIMIT = 50  # KL-10
COPIES_MIN, COPIES_MAX = 1, 50  # KL-19
BARCODE_MAX_ID = 99_999_999  # KL-42: eight digits
# Holds the unique barcode column between the insert and the id-based
# barcode; never committed (phase 3 small decision 3).
_PENDING_BARCODE = "PENDING-"
_BOOK_FIELDS = frozenset({"title", "author", "isbn13", "publisher", "year"})


def suggestion_message(suggestion: str) -> str:
    """Plan G07: the text shown with the ``isbn_accept`` button."""
    return f"Kontrol hanesi hatalı. Bunu mu demek istediniz: {suggestion}"


def _clean_isbn(raw: str | None) -> str | None:
    if raw is None or not raw.strip():
        return None
    result = parse_isbn(raw)
    if isinstance(result, IsbnOk):
        return result.isbn13
    if isinstance(result, IsbnSuggest):
        raise RuleViolation(suggestion_message(result.suggestion))
    raise RuleViolation(result.reason)


def _clean_book(
    title: str, author: str, isbn13: str | None, publisher: str | None, year: int | None
) -> dict[str, object]:
    title, author, publisher = title.strip(), author.strip(), (publisher or "").strip()
    if not title:
        raise RuleViolation("Başlık boş olamaz")
    if len(title) > 300:
        raise RuleViolation("Başlık en fazla 300 karakter olabilir")
    if not author:
        raise RuleViolation("Yazar boş olamaz")
    if len(author) > 300:
        raise RuleViolation("Yazar en fazla 300 karakter olabilir")
    if len(publisher) > 200:
        raise RuleViolation("Yayınevi en fazla 200 karakter olabilir")
    if year is not None and not 1 <= year <= 9999:
        raise RuleViolation("Yıl 1 ile 9999 arasında olmalı")
    return {
        "title": title,
        "author": author,
        "isbn13": _clean_isbn(isbn13),
        "publisher": publisher or None,
        "year": year,
    }


@require_role(Role.CLERK)
@transaction.atomic
def create_book(
    actor, title: str, author: str, isbn13: str | None, publisher: str | None, year: int | None
) -> Book:
    """``isbn13`` may be any form ``parse_isbn`` accepts; it is stored as
    ISBN-13. A suggestion is refused here: staff accept it in the form."""
    return Book.objects.create(**_clean_book(title, author, isbn13, publisher, year))


@require_role(Role.CLERK)
@transaction.atomic
def update_book(actor, book: Book, **fields: object) -> Book:
    unknown = fields.keys() - _BOOK_FIELDS
    if unknown:
        raise TypeError(f"unknown book fields: {sorted(unknown)}")
    current = {name: getattr(book, name) for name in _BOOK_FIELDS}
    cleaned = _clean_book(**{**current, **fields})
    for name, value in cleaned.items():
        setattr(book, name, value)
    book.save()
    return book


@require_role(Role.CLERK)
@transaction.atomic
def add_copies(actor, book: Book, n: int) -> list[Copy]:
    """Add ``n`` (1–50) copies on the shelf; each barcode is ``f"{id:08d}"``.

    An id above 99,999,999 raises "Barkod aralığı doldu" and the whole
    batch is rolled back (KL-42).
    """
    if not COPIES_MIN <= n <= COPIES_MAX:
        raise RuleViolation("Nüsha sayısı 1 ile 50 arasında olmalı")
    copies = []
    for _ in range(n):
        copy = Copy.objects.create(book=book, barcode=_PENDING_BARCODE, status=CopyStatus.ON_SHELF)
        if copy.id > BARCODE_MAX_ID:
            raise RuleViolation("Barkod aralığı doldu")
        copy.barcode = f"{copy.id:08d}"
        copy.save(update_fields=["barcode"])
        copies.append(copy)
    return copies


@transaction.atomic
def find_copy(barcode: str) -> Copy:
    copy = Copy.objects.select_related("book").filter(barcode=barcode).first()
    if copy is None:
        raise RuleViolation("Nüsha bulunamadı")
    return copy


@transaction.atomic
def get_book(pk: int) -> Book | None:
    return Book.objects.filter(pk=pk).first()


@transaction.atomic
def book_copies(book: Book) -> list[Copy]:
    return list(book.copies.order_by("barcode"))


def is_barcode(q: str) -> bool:
    """Eight ASCII digits: the copy barcode form (phase 3 small decision 3)."""
    return len(q) == 8 and q.isascii() and q.isdigit()


@transaction.atomic
def shelf_counts(books: list[Book]) -> dict[int, tuple[int, int]]:
    """Book id -> (copies on the shelf, all copies), in one query."""
    rows = (
        Copy.objects.filter(book__in=books)
        .values("book_id")
        .annotate(on_shelf=Count("pk", filter=Q(status=CopyStatus.ON_SHELF)), total=Count("pk"))
    )
    counts = {row["book_id"]: (row["on_shelf"], row["total"]) for row in rows}
    return {book.pk: counts.get(book.pk, (0, 0)) for book in books}


@transaction.atomic
def search_books(q: str, limit: int = SEARCH_LIMIT) -> list[Book]:
    """KL-10: a valid ISBN matches ``isbn13`` exactly and an 8-digit query a
    copy barcode exactly; ``search_key`` containing ``normalize_tr(q)`` is
    always searched too. Exact matches come first, then by title.
    """
    q = q.strip()
    text = normalize_tr(q)
    if not text:
        return []
    exact: list[Q] = []
    isbn = parse_isbn(q)
    if isinstance(isbn, IsbnOk):
        exact.append(Q(isbn13=isbn.isbn13))
    if is_barcode(q):
        exact.append(Q(pk__in=Copy.objects.filter(barcode=q).values("book_id")))
    condition = Q(search_key__contains=text)
    rank: Value | Case = Value(1)
    if exact:
        exact_match = functools.reduce(operator.or_, exact)
        condition |= exact_match
        rank = Case(When(exact_match, then=Value(0)), default=Value(1), output_field=IntegerField())
    matches = Book.objects.filter(condition).order_by(rank, "search_key", "pk")
    return list(matches[:limit])


# --- Labels (G08: FR-06, ADR-0036, KL-25) -------------------------------------

SELECTION_MAX = 240  # KL-25: ten label pages
RANGE_AND_LIST = "Aralık ya da seçim kutuları kullanın, ikisini birden değil"
START_AFTER_END = "Başlangıç bitişten büyük olamaz"
TOO_MANY = "En fazla 240 öğe seçilebilir"
TITLE_ON_LABEL = 30  # phase 4 small decision 3


def _blank(value: str | None) -> bool:
    return value is None or not value.strip()


@transaction.atomic
def copies_for_labels(
    copy_ids: list[int] | None, start: str | None, end: str | None
) -> list[int]:
    """Copy ids to print, ascending by barcode (KL-25).

    Either a barcode range (both ends, 8 digits, at most 240 wide) or the
    checkbox list (at most 240 ids). Unknown and WITHDRAWN copies are
    skipped; the server applies the same rule to the checkbox list.
    """
    has_list = bool(copy_ids)
    has_range = not (_blank(start) and _blank(end))
    if has_list and has_range:
        raise RuleViolation(RANGE_AND_LIST)
    if not (has_list or has_range):
        raise RuleViolation("En az bir nüsha seçin")
    printable = Copy.objects.exclude(status=CopyStatus.WITHDRAWN).order_by("barcode")
    if has_range:
        start, end = (start or "").strip(), (end or "").strip()
        if not (is_barcode(start) and is_barcode(end)):
            raise RuleViolation("Başlangıç ve bitiş 8 haneli barkod olmalı")
        if start > end:
            raise RuleViolation(START_AFTER_END)
        if int(end) - int(start) + 1 > SELECTION_MAX:
            raise RuleViolation(TOO_MANY)
        # Barcodes are zero-padded to eight digits, so text order is numeric order.
        ids = list(printable.filter(barcode__gte=start, barcode__lte=end).values_list("pk", flat=True))
        if not ids:
            raise RuleViolation("Aralıkta basılacak nüsha yok")
        return ids
    wanted = set(copy_ids or [])
    if len(wanted) > SELECTION_MAX:
        raise RuleViolation(TOO_MANY)
    ids = list(printable.filter(pk__in=wanted).values_list("pk", flat=True))
    if not ids:
        raise RuleViolation("En az bir nüsha seçin")
    return ids


@transaction.atomic
def label_pdf(copy_ids: list[int]) -> bytes:
    """One label per copy, in the given order: library name, barcode, code
    and the first 30 characters of the title (phase 4 small decision 3)."""
    library_name = get_settings().library_name
    copies = Copy.objects.select_related("book").in_bulk(copy_ids)
    items = [
        SheetItem(
            header=library_name,
            barcode_value=copies[pk].barcode,
            caption=copies[pk].barcode,
            footer=copies[pk].book.title[:TITLE_ON_LABEL],
        )
        for pk in copy_ids
        if pk in copies
    ]
    return render_sheet(items, LABEL_LAYOUT)
