"""View tests for books and copies (G07).

TC-62, TC-63, TC-66; plus the search, create, edit, detail and add-copies
screens.
"""

from __future__ import annotations

import pytest
from django.test import Client

from accounts.models import Role
from catalog.models import Book, Copy, CopyStatus
from tests.support.factories import make_book, make_copy, make_staff

pytestmark = pytest.mark.django_db

SUGGESTION = "Kontrol hanesi hatalı. Bunu mu demek istediniz: 9786053609322"


@pytest.fixture
def clerk_client(client: Client) -> Client:
    client.force_login(make_staff("ali", role=Role.CLERK))
    return client


def _book_data(**overrides) -> dict[str, str]:
    data = {"title": "Hayvan Çiftliği", "author": "George Orwell", "isbn": "", "publisher": "", "year": ""}
    data.update(overrides)
    return data


# --- ISBN suggestion flow (TC-62, TC-63) --------------------------------------


def test_tc62_isbn_suggestion_then_acceptance(clerk_client) -> None:
    response = clerk_client.post("/kitaplar/yeni/", _book_data(isbn="6053609322"))
    html = response.content.decode()
    assert response.status_code == 200
    assert Book.objects.count() == 0
    assert SUGGESTION in html
    assert 'name="isbn_accept" value="9786053609322"' in html
    response = clerk_client.post(
        "/kitaplar/yeni/", _book_data(isbn="6053609322", isbn_accept="9786053609322")
    )
    book = Book.objects.get()
    assert response.status_code == 302
    assert response["Location"] == f"/kitaplar/{book.pk}/"
    assert book.isbn13 == "9786053609322"


def test_tc63_invalid_isbn_shows_an_error_and_no_suggestion(clerk_client) -> None:
    response = clerk_client.post("/kitaplar/yeni/", _book_data(isbn="6053609321"))
    html = response.content.decode()
    assert response.status_code == 200
    assert Book.objects.count() == 0
    assert "ISBN kontrol hanesi hatalı" in html
    assert "isbn_accept" not in html
    assert "Bunu mu demek istediniz" not in html


def test_accepted_value_is_validated_again(clerk_client) -> None:
    response = clerk_client.post(
        "/kitaplar/yeni/", _book_data(isbn="6053609322", isbn_accept="9786053609321")
    )
    assert response.status_code == 200
    assert "ISBN kontrol hanesi hatalı" in response.content.decode()
    assert Book.objects.count() == 0


def test_create_book_without_isbn(clerk_client) -> None:
    assert clerk_client.get("/kitaplar/yeni/").status_code == 200
    response = clerk_client.post("/kitaplar/yeni/", _book_data(year="1945", publisher="Can"))
    book = Book.objects.get()
    assert response.status_code == 302
    assert (book.isbn13, book.year, book.publisher) == (None, 1945, "Can")
    assert "Kitap kaydedildi" in clerk_client.get(response["Location"]).content.decode()


def test_create_book_form_error(clerk_client) -> None:
    response = clerk_client.post("/kitaplar/yeni/", _book_data(title=""))
    assert response.status_code == 200
    assert Book.objects.count() == 0


def test_edit_book_with_suggestion(clerk_client) -> None:
    book = make_book("Tutunamayanlar", "Oğuz Atay")
    response = clerk_client.get(f"/kitaplar/{book.pk}/duzenle/")
    assert response.status_code == 200
    assert "Tutunamayanlar" in response.content.decode()
    data = _book_data(title="Tutunamayanlar", author="Oğuz Atay", isbn="6053609322")
    response = clerk_client.post(f"/kitaplar/{book.pk}/duzenle/", data)
    assert response.status_code == 200
    assert SUGGESTION in response.content.decode()
    data["isbn_accept"] = "9786053609322"
    response = clerk_client.post(f"/kitaplar/{book.pk}/duzenle/", data)
    assert response.status_code == 302
    assert response["Location"] == f"/kitaplar/{book.pk}/"
    book.refresh_from_db()
    assert book.isbn13 == "9786053609322"


def test_edit_form_shows_the_stored_isbn(clerk_client) -> None:
    book = make_book(isbn13="9786053609322")
    assert 'value="9786053609322"' in clerk_client.get(f"/kitaplar/{book.pk}/duzenle/").content.decode()


# --- Search (TC-66) -----------------------------------------------------------


def test_tc66_barcode_search_shows_book_and_copy_status(clerk_client) -> None:
    book = make_book("Tutunamayanlar", "Oğuz Atay")
    make_copy(book, pk=42)
    response = clerk_client.get("/kitaplar/", {"q": "00000042"})
    html = response.content.decode()
    assert response.status_code == 200
    assert "Tutunamayanlar" in html
    assert "Rafta" in html
    assert f'href="/kitaplar/{book.pk}/"' in html


def test_search_without_query_shows_the_form(clerk_client) -> None:
    html = clerk_client.get("/kitaplar/").content.decode()
    assert 'name="q"' in html
    assert "Sonuç yok." not in html


def test_search_without_matches(clerk_client) -> None:
    make_book()
    html = clerk_client.get("/kitaplar/", {"q": "99999998"}).content.decode()
    assert "Sonuç yok." in html


def test_eight_digit_title_match_without_such_copy(clerk_client) -> None:
    make_book("Kod 12345678", "Yazar")
    html = clerk_client.get("/kitaplar/", {"q": "12345678"}).content.decode()
    assert "Kod 12345678" in html
    assert "Nüsha 12345678" not in html


def test_search_lists_shelf_counts(clerk_client) -> None:
    book = make_book("Tutunamayanlar", "Oğuz Atay")
    make_copy(book)
    make_copy(book, status=CopyStatus.ON_LOAN)
    html = clerk_client.get("/kitaplar/", {"q": "oguz"}).content.decode()
    assert "1 / 2" in html


# --- Detail and copies --------------------------------------------------------


def test_detail_lists_copies_with_barcode_and_status(clerk_client) -> None:
    book = make_book("Tutunamayanlar", "Oğuz Atay", isbn13="9786053609322")
    make_copy(book, pk=42)
    make_copy(book, pk=43, status=CopyStatus.DAMAGED)
    html = clerk_client.get(f"/kitaplar/{book.pk}/").content.decode()
    for text in ("Tutunamayanlar", "Oğuz Atay", "9786053609322", "00000042", "Rafta", "00000043", "Hasarlı"):
        assert text in html
    assert f'href="/kitaplar/{book.pk}/duzenle/"' in html


def test_add_copies_from_the_detail_page(clerk_client) -> None:
    book = make_book()
    response = clerk_client.post(f"/kitaplar/{book.pk}/nusha/", {"count": "3"})
    assert response.status_code == 302
    assert response["Location"] == f"/kitaplar/{book.pk}/"
    assert Copy.objects.filter(book=book).count() == 3
    assert "3 nüsha eklendi" in clerk_client.get(response["Location"]).content.decode()


@pytest.mark.parametrize("count", ["0", "51"])
def test_add_copies_out_of_range_reshows_the_detail_with_200(clerk_client, count) -> None:
    book = make_book()
    response = clerk_client.post(f"/kitaplar/{book.pk}/nusha/", {"count": count})
    assert response.status_code == 200
    assert "Nüsha sayısı 1 ile 50 arasında olmalı" in response.content.decode()
    assert Copy.objects.count() == 0


def test_add_copies_needs_a_number(clerk_client) -> None:
    book = make_book()
    response = clerk_client.post(f"/kitaplar/{book.pk}/nusha/", {"count": "iki"})
    assert response.status_code == 200
    assert Copy.objects.count() == 0


def test_unknown_book_is_404(clerk_client) -> None:
    assert clerk_client.get("/kitaplar/99/").status_code == 404
    assert clerk_client.get("/kitaplar/99/duzenle/").status_code == 404
    assert clerk_client.post("/kitaplar/99/nusha/", {"count": "1"}).status_code == 404


def test_add_copies_is_post_only(clerk_client) -> None:
    book = make_book()
    assert clerk_client.get(f"/kitaplar/{book.pk}/nusha/").status_code == 405


def test_book_pages_need_login(client: Client) -> None:
    assert client.get("/kitaplar/").status_code == 302


def test_home_links_to_books(clerk_client) -> None:
    assert 'href="/kitaplar/"' in clerk_client.get("/").content.decode()


# --- Labels (G08: TC-269) -------------------------------------------------------


def test_tc269_label_range_form(clerk_client) -> None:
    response = clerk_client.get("/nushalar/etiket/")
    html = response.content.decode()
    assert response.status_code == 200
    assert 'name="start"' in html and 'name="end"' in html


def test_tc269_label_pdf_from_a_range(clerk_client) -> None:
    make_copy(pk=1)
    response = clerk_client.post("/nushalar/etiket/", {"start": "00000001", "end": "00000001"})
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response["Content-Disposition"] == 'inline; filename="etiketler.pdf"'
    assert response.content.startswith(b"%PDF")


def test_tc269_label_pdf_from_checkboxes(clerk_client) -> None:
    book = make_book()
    make_copy(book, pk=1)
    make_copy(book, pk=2)
    response = clerk_client.post("/nushalar/etiket/", {"copy_ids": ["2", "1"]})
    assert response.status_code == 200
    assert response["Content-Disposition"] == 'inline; filename="etiketler.pdf"'


def test_tc269_withdrawn_copy_has_no_checkbox_on_the_book_page(clerk_client) -> None:
    book = make_book()
    make_copy(book, pk=1)
    make_copy(book, pk=2, status=CopyStatus.WITHDRAWN)
    html = clerk_client.get(f"/kitaplar/{book.pk}/").content.decode()
    assert 'name="copy_ids" value="1"' in html
    assert 'name="copy_ids" value="2"' not in html
    assert 'action="/nushalar/etiket/"' in html
    assert "Etiket bas</button>" in html


def test_label_selection_error_reshows_the_range_form_with_200(clerk_client) -> None:
    response = clerk_client.post("/nushalar/etiket/", {})
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    assert "En az bir nüsha seçin" in response.content.decode()


def test_label_selection_with_bad_ids_is_refused(clerk_client) -> None:
    response = clerk_client.post("/nushalar/etiket/", {"copy_ids": ["x"]})
    assert response.status_code == 200
    assert "Geçersiz seçim" in response.content.decode()


def test_no_label_button_when_every_copy_is_withdrawn(clerk_client) -> None:
    book = make_book()
    make_copy(book, status=CopyStatus.WITHDRAWN)
    html = clerk_client.get(f"/kitaplar/{book.pk}/").content.decode()
    assert "Etiket bas</button>" not in html
