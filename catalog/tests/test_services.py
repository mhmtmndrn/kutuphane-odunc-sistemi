"""Service tests for books and copies (G07).

TC-60, TC-61, TC-64, TC-65, TC-67, TC-68, TC-262…TC-264; plus updates,
``find_copy`` and the derived ``search_key`` and ``status_changed_at``.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone as dt_timezone

import pytest
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection, transaction

from accounts.models import Role
from administration.errors import RuleViolation
from catalog import services
from catalog.models import Book, Copy, CopyStatus
from tests.support.clock import FrozenClock
from tests.support.factories import make_book, make_copy, make_staff

pytestmark = pytest.mark.django_db


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK)


def set_copy_sequence(last_id: int) -> None:
    """The next copy id becomes ``last_id + 1`` (SQLite AUTOINCREMENT)."""
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = %s", ["copy"])
        cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES (%s, %s)", ["copy", last_id])


# --- Books (FR-04) ------------------------------------------------------------


def test_tc60_isbn_is_stored_normalized_or_null(clerk) -> None:
    first = services.create_book(
        clerk, "Hayvan Çiftliği", "George Orwell", "978-605-360-932-2", "Can Yayınları", 2020
    )
    second = services.create_book(clerk, "Tutunamayanlar", "Oğuz Atay", None, None, None)
    first.refresh_from_db()
    second.refresh_from_db()
    assert first.isbn13 == "9786053609322"
    assert (first.publisher, first.year) == ("Can Yayınları", 2020)
    assert second.isbn13 is None
    assert second.publisher is None and second.year is None


@pytest.mark.parametrize(
    ("title", "author", "message"),
    [("", "Oğuz Atay", "Başlık boş olamaz"), ("Tutunamayanlar", "  ", "Yazar boş olamaz")],
)
def test_tc61_blank_title_or_author_is_refused(clerk, title, author, message) -> None:
    with pytest.raises(RuleViolation) as exc:
        services.create_book(clerk, title, author, None, None, None)
    assert exc.value.message == message
    assert Book.objects.count() == 0


def test_create_book_converts_isbn10_and_trims(clerk) -> None:
    book = services.create_book(clerk, " Tutunamayanlar ", " Oğuz Atay ", "0306406152", " ", None)
    assert (book.title, book.author, book.isbn13, book.publisher) == (
        "Tutunamayanlar",
        "Oğuz Atay",
        "9780306406157",
        None,
    )


@pytest.mark.parametrize(
    ("isbn", "message"),
    [
        ("6053609321", "ISBN kontrol hanesi hatalı"),
        ("12345", "ISBN 10 ya da 13 haneli olmalı"),
        ("6053609322", "Kontrol hanesi hatalı. Bunu mu demek istediniz: 9786053609322"),
    ],
)
def test_create_book_refuses_isbns_that_are_not_ok(clerk, isbn, message) -> None:
    with pytest.raises(RuleViolation) as exc:
        services.create_book(clerk, "Tutunamayanlar", "Oğuz Atay", isbn, None, None)
    assert exc.value.message == message
    assert Book.objects.count() == 0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("title", "A" * 301, "Başlık en fazla 300 karakter olabilir"),
        ("author", "A" * 301, "Yazar en fazla 300 karakter olabilir"),
        ("publisher", "A" * 201, "Yayınevi en fazla 200 karakter olabilir"),
        ("year", 0, "Yıl 1 ile 9999 arasında olmalı"),
        ("year", 10000, "Yıl 1 ile 9999 arasında olmalı"),
    ],
)
def test_create_book_bounds(clerk, field, value, message) -> None:
    values = {"title": "T", "author": "A", "isbn13": None, "publisher": None, "year": None}
    values[field] = value
    with pytest.raises(RuleViolation) as exc:
        services.create_book(clerk, **values)
    assert exc.value.message == message


def test_create_book_accepts_the_bounds(clerk) -> None:
    book = services.create_book(clerk, "T" * 300, "A" * 300, None, "P" * 200, 9999)
    assert book.year == 9999
    assert services.create_book(clerk, "T", "A", None, None, 1).year == 1


def test_create_book_requires_an_active_staff_actor() -> None:
    with pytest.raises(PermissionDenied):
        services.create_book(make_staff("eski", is_active=False), "T", "A", None, None, None)


def test_update_book_changes_fields_and_search_key(clerk) -> None:
    book = make_book("Tutunamayanlar", "Oğuz Atay")
    services.update_book(clerk, book, title="Tehlikeli Oyunlar", isbn13="978-0-306-40615-7", year=1973)
    book.refresh_from_db()
    assert (book.title, book.isbn13, book.year) == ("Tehlikeli Oyunlar", "9780306406157", 1973)
    assert book.search_key == "tehlikeli oyunlar oguz atay"


def test_update_book_can_clear_isbn(clerk) -> None:
    book = make_book(isbn13="9780306406157")
    services.update_book(clerk, book, isbn13="")
    book.refresh_from_db()
    assert book.isbn13 is None


def test_update_book_validates(clerk) -> None:
    book = make_book("Tutunamayanlar")
    with pytest.raises(RuleViolation):
        services.update_book(clerk, book, title=" ")
    book.refresh_from_db()
    assert book.title == "Tutunamayanlar"


def test_update_book_refuses_unknown_fields(clerk) -> None:
    with pytest.raises(TypeError):
        services.update_book(clerk, make_book(), search_key="x")


def test_book_search_key_folds_title_and_author() -> None:
    assert make_book("İstanbul Hatırası", "Ahmet Ümit").search_key == "istanbul hatirasi ahmet umit"


def test_isbn13_column_requires_13_characters() -> None:
    book = make_book()
    with pytest.raises(IntegrityError), transaction.atomic():
        Book.objects.filter(pk=book.pk).update(isbn13="123")


# --- Copies (FR-05, KL-19, KL-42) ---------------------------------------------


def test_tc64_two_copies_get_distinct_barcodes_on_shelf(clerk) -> None:
    book = make_book()
    copies = services.add_copies(clerk, book, 2)
    assert len(copies) == 2
    for copy in copies:
        copy.refresh_from_db()
        assert copy.barcode == f"{copy.id:08d}"
        assert copy.status == CopyStatus.ON_SHELF
        assert copy.book == book
    assert copies[0].barcode != copies[1].barcode


@pytest.mark.parametrize(("last_id", "barcode"), [(0, "00000001"), (41, "00000042"), (99999998, "99999999")])
def test_tc65_barcode_is_the_zero_padded_id(clerk, last_id, barcode) -> None:
    set_copy_sequence(last_id)
    (copy,) = services.add_copies(clerk, make_book(), 1)
    assert copy.id == last_id + 1
    assert Copy.objects.get(pk=copy.pk).barcode == barcode


@pytest.mark.parametrize("n", [0, 51, -1])
def test_tc262_copy_count_outside_1_to_50_is_refused(clerk, n) -> None:
    with pytest.raises(RuleViolation) as exc:
        services.add_copies(clerk, make_book(), n)
    assert exc.value.message == "Nüsha sayısı 1 ile 50 arasında olmalı"
    assert Copy.objects.count() == 0


@pytest.mark.parametrize("n", [1, 50])
def test_tc262_copy_count_bounds_are_accepted(clerk, n) -> None:
    assert len(services.add_copies(clerk, make_book(), n)) == n
    assert Copy.objects.count() == n
    assert len(set(Copy.objects.values_list("barcode", flat=True))) == n


def test_tc263_barcode_overflow_rolls_back(clerk) -> None:
    set_copy_sequence(99999998)  # first new id fits, the second does not
    book = make_book()
    with pytest.raises(RuleViolation) as exc:
        services.add_copies(clerk, book, 2)
    assert exc.value.message == "Barkod aralığı doldu"
    assert Copy.objects.count() == 0


def test_find_copy(clerk) -> None:
    copy = make_copy(make_book(), pk=42)
    assert services.find_copy("00000042") == copy
    with pytest.raises(RuleViolation) as exc:
        services.find_copy("00000043")
    assert exc.value.message == "Nüsha bulunamadı"


def test_copy_status_change_updates_status_changed_at(monkeypatch) -> None:
    clock = FrozenClock(monkeypatch, datetime(2026, 11, 16, 9, 0, tzinfo=dt_timezone.utc))
    copy = make_copy(make_book())
    assert copy.status_changed_at == clock.now()
    clock.advance(hours=1)
    copy.save()
    assert Copy.objects.get(pk=copy.pk).status_changed_at == clock.now() - timedelta(hours=1)
    copy.status = CopyStatus.ON_LOAN
    copy.save()
    assert Copy.objects.get(pk=copy.pk).status_changed_at == clock.now()
    fetched = Copy.objects.get(pk=copy.pk)
    clock.advance(hours=1)
    fetched.status = CopyStatus.ON_SHELF
    fetched.save(update_fields=["status"])
    assert Copy.objects.get(pk=copy.pk).status_changed_at == clock.now()


def test_copy_status_values_are_checked() -> None:
    copy = make_copy(make_book())
    with pytest.raises(IntegrityError), transaction.atomic():
        Copy.objects.filter(pk=copy.pk).update(status="GONE")


def test_book_with_copies_cannot_be_deleted() -> None:
    from django.db.models import ProtectedError

    copy = make_copy(make_book())
    with pytest.raises(ProtectedError):
        copy.book.delete()


# --- Search (FR-04, KL-10, NFR-10) --------------------------------------------


@pytest.mark.parametrize("q", ["istanbul", "İSTANBUL", "İstanbul", "umit", "9786053609322"])
def test_tc67_title_author_and_isbn_search(q) -> None:
    book = make_book("İstanbul Hatırası", "Ahmet Ümit", isbn13="9786053609322")
    make_book("Tutunamayanlar", "Oğuz Atay")
    assert services.search_books(q) == [book]


def test_tc68_unknown_barcode_and_renamed_title(clerk) -> None:
    book = make_book("Tutunamayanlar", "Oğuz Atay")
    make_copy(book, pk=42)
    assert services.search_books("99999998") == []
    services.update_book(clerk, book, title="Tehlikeli Oyunlar")
    assert services.search_books("tehlikeli") == [book]
    assert services.search_books("tutunamayanlar") == []


@pytest.mark.parametrize("q", ["0306406152", "978-0-306-40615-7"])
def test_tc264_isbn_forms_find_the_book(q) -> None:
    book = make_book("Yazılım Mühendisliği", "Ian Sommerville", isbn13="9780306406157")
    make_book("Başka Kitap", "Başka Yazar", isbn13="9786053609322")
    assert services.search_books(q) == [book]


def test_tc264_barcode_finds_the_copys_book() -> None:
    make_book("Yazılım Mühendisliği", "Ian Sommerville", isbn13="9780306406157")
    other = make_book("Tutunamayanlar", "Oğuz Atay")
    make_copy(other, pk=42)
    assert services.search_books("00000042") == [other]


def test_tc264_word_search_returns_at_most_50() -> None:
    for i in range(60):
        make_book(f"Deniz Kitabı {i}", "Yazar")
    assert len(services.search_books("deniz")) == 50


def test_isbn_and_barcode_matches_are_listed_first() -> None:
    # The title of "Aaa" contains the barcode digits; the barcode match comes first.
    by_title = make_book("Aaa 00000042", "Yazar")
    by_barcode = make_book("Zzz", "Yazar")
    make_copy(by_barcode, pk=42)
    assert services.search_books("00000042") == [by_barcode, by_title]


def test_book_with_several_matching_copies_is_listed_once() -> None:
    book = make_book("Tutunamayanlar", "Oğuz Atay")
    make_copy(book)
    make_copy(book)
    assert services.search_books("tutunamayanlar") == [book]


def test_empty_book_query_returns_nothing() -> None:
    make_book()
    assert services.search_books("   ") == []


def test_like_wildcards_are_literal_in_book_search() -> None:
    make_book("Tutunamayanlar", "Oğuz Atay")
    assert services.search_books("%") == []


# --- Labels (G08: FR-06, ADR-0036, KL-25) --------------------------------------

from administration import services as admin_services  # noqa: E402
from tests.support.barcode import pdf_page_count, pdf_text, read_pdf_barcodes  # noqa: E402

RANGE_AND_LIST = "Aralık ya da seçim kutuları kullanın, ikisini birden değil"
NOTHING_SELECTED = "En az bir nüsha seçin"
TOO_MANY = "En fazla 240 öğe seçilebilir"


def _copies(ids, status_by_id=None) -> dict[int, Copy]:
    book = make_book()
    status_by_id = status_by_id or {}
    return {i: make_copy(book, pk=i, status=status_by_id.get(i, CopyStatus.ON_SHELF)) for i in ids}


def test_tc265_range_skips_missing_and_withdrawn_copies() -> None:
    _copies([10, 11, 13, 14, 15], {13: CopyStatus.WITHDRAWN})
    assert services.copies_for_labels(None, "00000010", "00000015") == [10, 11, 14, 15]


def test_range_includes_lost_damaged_and_lent_copies() -> None:
    _copies([1, 2, 3], {1: CopyStatus.LOST, 2: CopyStatus.DAMAGED, 3: CopyStatus.ON_LOAN})
    assert services.copies_for_labels(None, "00000001", "00000003") == [1, 2, 3]


@pytest.mark.parametrize(
    ("args", "message"),
    [
        ((None, "00000015", "00000010"), "Başlangıç bitişten büyük olamaz"),
        ((None, "00000001", "00000241"), TOO_MANY),
        ((list(range(1, 242)), None, None), TOO_MANY),
        ((None, "00000100", "00000105"), "Aralıkta basılacak nüsha yok"),
    ],
)
def test_tc266_range_and_size_refusals(args, message) -> None:
    _copies([1, 2])
    with pytest.raises(RuleViolation) as exc:
        services.copies_for_labels(*args)
    assert exc.value.message == message


def test_tc266_range_of_240_is_accepted() -> None:
    _copies([1, 240])
    assert services.copies_for_labels(None, "00000001", "00000240") == [1, 240]


def test_tc266_range_with_only_withdrawn_copies_is_empty() -> None:
    _copies([5], {5: CopyStatus.WITHDRAWN})
    with pytest.raises(RuleViolation) as exc:
        services.copies_for_labels(None, "00000005", "00000005")
    assert exc.value.message == "Aralıkta basılacak nüsha yok"


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (([1], "00000001", "00000002"), RANGE_AND_LIST),
        (([1], "00000001", None), RANGE_AND_LIST),
        ((None, None, None), NOTHING_SELECTED),
        (([], "", ""), NOTHING_SELECTED),
    ],
)
def test_tc267_range_and_list_together_or_neither(args, message) -> None:
    _copies([1, 2])
    with pytest.raises(RuleViolation) as exc:
        services.copies_for_labels(*args)
    assert exc.value.message == message


def test_tc267_withdrawn_copy_in_the_list_is_skipped() -> None:
    _copies([1, 2, 3], {2: CopyStatus.WITHDRAWN})
    assert services.copies_for_labels([3, 2, 1, 99, 3], None, None) == [1, 3]


def test_list_of_only_withdrawn_or_unknown_copies_selects_nothing() -> None:
    _copies([2], {2: CopyStatus.WITHDRAWN})
    with pytest.raises(RuleViolation) as exc:
        services.copies_for_labels([2, 99], None, None)
    assert exc.value.message == NOTHING_SELECTED


@pytest.mark.parametrize(("start", "end"), [("1", "00000002"), ("00000001", ""), ("0000000a", "00000002")])
def test_range_ends_must_be_eight_digit_barcodes(start, end) -> None:
    with pytest.raises(RuleViolation) as exc:
        services.copies_for_labels(None, start, end)
    assert exc.value.message == "Başlangıç ve bitiş 8 haneli barkod olmalı"


def test_tc72_label_holds_library_name_code_and_first_30_title_characters() -> None:
    admin_services.get_settings()
    title_30 = "Saatleri Ayarlama Enstitüsü 12"
    assert len(title_30) == 30
    short = make_copy(make_book(title_30), pk=7)
    long_ = make_copy(make_book(title_30 + "X"), pk=8)
    text = pdf_text(services.label_pdf([short.pk, long_.pk]))
    assert "Kütüphane" in text
    assert "00000007" in text and "00000008" in text
    assert text.count(title_30) == 2
    assert "X" not in text


def test_tc73_long_library_name_is_shortened_on_labels(monkeypatch) -> None:
    settings = admin_services.get_settings()
    settings.library_name = "W" * 80
    settings.save()
    text = pdf_text(services.label_pdf([make_copy(pk=1).pk]))
    assert "…" in text
    assert "W" * 80 not in text


def test_label_pdf_follows_the_given_order_and_layout() -> None:
    copies = _copies(range(1, 26))
    pdf = services.label_pdf([c.pk for c in copies.values()])
    assert pdf.startswith(b"%PDF")
    assert pdf_page_count(pdf) == 2


@pytest.mark.slow
def test_tc71_thirty_labels_from_several_books_decode_in_order() -> None:
    first, second, third = make_book("Birinci"), make_book("İkinci"), make_book("Üçüncü")
    ids = []
    for i in range(30):
        ids.append(make_copy((first, second, third)[i % 3], pk=100 + i).pk)
    selected = services.copies_for_labels(None, "00000100", "00000129")
    assert selected == ids
    pdf = services.label_pdf(selected)
    assert pdf_page_count(pdf) == 2
    decoded = read_pdf_barcodes(pdf)
    assert [b.value for b in decoded] == [f"{i:08d}" for i in ids]
    assert [b.page for b in decoded] == [0] * 24 + [1] * 6
    assert {b.format for b in decoded} == {"Code128"}
