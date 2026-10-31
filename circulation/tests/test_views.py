"""Circulation view tests (G11): TC-127…TC-130, TC-135, TC-281…TC-284; plus
the renewal route, the check-in search and the focus attributes (NFR-11)."""

from __future__ import annotations

import re
from datetime import date

import pytest
from django.test import Client

from accounts.models import Role
from administration import clock
from administration.models import ClosedDate
from billing.models import EntryKind, LedgerEntry
from catalog.models import CopyStatus
from circulation.models import Loan
from tests.support.factories import (
    make_book,
    make_charge,
    make_copy,
    make_loan,
    make_member,
    make_staff,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def today(monkeypatch: pytest.MonkeyPatch):
    def set_today(day: date) -> None:
        monkeypatch.setattr(clock, "today", lambda: day)

    set_today(date(2026, 11, 2))
    return set_today


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK)


@pytest.fixture
def clerk_client(client: Client, clerk) -> Client:
    client.force_login(clerk)
    return client


@pytest.fixture
def member():
    return make_member("Ayşe Yılmaz", "0555 111 22 33", member_no=1042)


def _body(response) -> str:
    return response.content.decode()


def _autofocused(body: str) -> list[str]:
    """``name`` of every element with ``autofocus`` (or the button text)."""
    names = []
    for tag in re.findall(r"<(?:input|button|select)[^>]*\bautofocus\b[^>]*>", body):
        match = re.search(r'name="([^"]+)"', tag)
        names.append(match.group(1) if match else tag)
    return names


def _confirm_button(body: str) -> bool:
    return 'method="post" action="/odunc/"' in body


# --- Check-out screen (FR-07, FR-08, FR-11, NFR-11) ------------------------------


def test_empty_checkout_screen_focuses_the_member_field(today, clerk_client) -> None:
    response = clerk_client.get("/odunc/")
    assert response.status_code == 200
    body = _body(response)
    assert _autofocused(body) == ["uye"]
    assert 'src="/static/js/scan.js"' in body


def test_tc128_scan_member_preview_and_confirm(today, clerk_client, member) -> None:
    copy = make_copy(make_book("Tutunamayanlar"), pk=42)
    make_loan(member, loaned_on=date(2026, 10, 30))
    response = clerk_client.get("/odunc/?uye=1042")
    body = _body(response)
    assert response.status_code == 200
    assert "Ayşe Yılmaz" in body and "Üye 1042" in body
    assert _autofocused(body) == ["nusha"]
    assert 'data-next-focus="id_nusha"' in body
    assert "Uzat" in body  # the open loan's renewal button

    preview = _body(clerk_client.get("/odunc/?uye=1042&nusha=00000042"))
    assert "Tutunamayanlar" in preview and "Son tarih 16.11.2026" in preview
    assert _confirm_button(preview)
    assert '<button type="submit" autofocus>Onayla</button>' in preview
    assert len(_autofocused(preview)) == 1

    response = clerk_client.post("/odunc/", {"uye": "1042", "nusha": "00000042"})
    assert response.status_code == 303
    assert response["Location"] == "/odunc/"
    after = _body(clerk_client.get("/odunc/"))
    assert "Son tarih 16.11.2026" in after
    assert _autofocused(after) == ["uye"]
    copy.refresh_from_db()
    assert copy.status == CopyStatus.ON_LOAN


def test_tc127_blocked_post_reshows_the_screen(today, clerk_client, member) -> None:
    make_charge(member, EntryKind.FINE, 5000)
    copy = make_copy(pk=42)
    response = clerk_client.post("/odunc/", {"uye": "1042", "nusha": copy.barcode})
    assert response.status_code == 200
    body = _body(response)
    assert "Borç eşiği aşıldı" in body
    assert "Ayşe Yılmaz" in body
    assert not Loan.objects.exists()


def test_blocked_preview_has_no_confirm_button(today, clerk_client, member) -> None:
    make_charge(member, EntryKind.FINE, 5000)
    make_copy(pk=42)
    body = _body(clerk_client.get("/odunc/?uye=1042&nusha=00000042"))
    assert "Borç eşiği aşıldı" in body
    assert not _confirm_button(body)


def test_tc284_all_blockers_in_order(today, clerk_client) -> None:
    member = make_member("Pasif Üye", member_no=5, is_active=False)
    for _ in range(3):
        make_loan(member, loaned_on=date(2026, 11, 1))
    make_charge(member, EntryKind.FINE, 6000)
    copy = make_copy(pk=42)
    response = clerk_client.post("/odunc/", {"uye": "5", "nusha": copy.barcode})
    assert response.status_code == 200
    assert "Üye pasif; Ödünç limiti dolu; Borç eşiği aşıldı" in _body(response)
    assert Loan.objects.count() == 3


def test_tc129_name_search_then_checkout(today, clerk_client, member) -> None:
    make_member("Ayşe Kaya", member_no=7)
    copy = make_copy(pk=42)
    body = _body(clerk_client.get("/odunc/?uye=ayşe"))
    assert 'href="/odunc/?uye=1042"' in body and 'href="/odunc/?uye=7"' in body
    response = clerk_client.post("/odunc/", {"uye": "1042", "nusha": copy.barcode})
    assert response.status_code == 303
    assert Loan.objects.get().member == member


def test_tc130_unknown_member_unknown_copy_and_padded_barcode(today, clerk_client, member) -> None:
    make_copy(make_book("Saatleri Ayarlama Enstitüsü"), pk=42)
    body = _body(clerk_client.get("/odunc/?uye=999999"))
    assert "Üye bulunamadı" in body and 'name="nusha"' not in body
    body = _body(clerk_client.get("/odunc/?uye=1042&nusha=99999999"))
    assert "Nüsha bulunamadı" in body and not _confirm_button(body)
    response = clerk_client.post("/odunc/", {"uye": "1042", "nusha": "99999999"})
    assert response.status_code == 200 and "Nüsha bulunamadı" in _body(response)
    body = _body(clerk_client.get("/odunc/?uye=1042&nusha=%2000000042"))
    assert "Saatleri Ayarlama Enstitüsü" in body and _confirm_button(body)
    assert not Loan.objects.exists()


def test_tc281_copy_barcode_in_the_member_field(today, clerk_client) -> None:
    make_member("Kırk İki", member_no=42)
    make_copy(pk=42)
    body = _body(clerk_client.get("/odunc/?uye=00000042"))
    assert "Bu bir nüsha barkodu. Üye kartını okutun." in body
    assert "Kırk İki" not in body
    assert 'name="nusha"' not in body and not _confirm_button(body)


def test_tc282_phone_and_name_list_without_opening(today, clerk_client, member) -> None:
    make_member("Ayşe Kaya", "0532 000 00 00", member_no=7)
    body = _body(clerk_client.get("/odunc/?uye=0555 111 22 33"))
    assert 'href="/odunc/?uye=1042"' in body
    assert 'name="nusha"' not in body  # a single match is still only listed
    body = _body(clerk_client.get("/odunc/?uye=ayşe"))
    assert 'href="/odunc/?uye=1042"' in body and 'href="/odunc/?uye=7"' in body
    assert 'name="nusha"' not in body


def test_member_search_without_match(today, clerk_client) -> None:
    assert "Üye bulunamadı" in _body(clerk_client.get("/odunc/?uye=zeynep"))


def test_copy_search_lists_shelf_copies(today, clerk_client, member) -> None:
    book = make_book("Kürk Mantolu Madonna", "Sabahattin Ali")
    shelf = make_copy(book, pk=42)
    make_copy(book, pk=43, status=CopyStatus.LOST)
    body = _body(clerk_client.get("/odunc/?uye=1042&nusha=kürk"))
    assert f'href="/odunc/?uye=1042&amp;nusha={shelf.barcode}"' in body
    assert "00000043" not in body
    assert "Nüsha bulunamadı" in _body(clerk_client.get("/odunc/?uye=1042&nusha=yok"))


def test_post_with_bad_member_number(today, clerk_client) -> None:
    response = clerk_client.post("/odunc/", {"uye": "abc", "nusha": "00000042"})
    assert response.status_code == 200
    assert "Üye bulunamadı" in _body(response)


# --- Renewal route (FR-10) -------------------------------------------------------


def test_renew_redirects_to_next(today, clerk_client, member) -> None:
    loan = make_loan(member, loaned_on=date(2026, 10, 30))
    response = clerk_client.post(f"/odunc/{loan.pk}/uzat/", {"next": "/uyeler/1042/"})
    assert response.status_code == 303
    assert response["Location"] == "/uyeler/1042/"
    loan.refresh_from_db()
    assert loan.renewed_on == date(2026, 11, 2)
    assert "Uzatıldı; yeni son tarih 27.11.2026" in _body(clerk_client.get("/uyeler/1042/"))


def test_renew_ignores_an_unsafe_next(today, clerk_client, member) -> None:
    loan = make_loan(member, loaned_on=date(2026, 10, 30))
    response = clerk_client.post(f"/odunc/{loan.pk}/uzat/", {"next": "https://example.com/"})
    assert response["Location"] == "/odunc/?uye=1042"


def test_renew_refusal_reshows_the_checkout_screen(today, clerk_client, member) -> None:
    loan = make_loan(member, loaned_on=date(2026, 10, 30), renewed_on=date(2026, 11, 1))
    response = clerk_client.post(f"/odunc/{loan.pk}/uzat/", {"next": "/uyeler/1042/"})
    assert response.status_code == 200
    body = _body(response)
    assert "Uzatma hakkı kullanıldı" in body and "Üye 1042" in body


def test_renew_unknown_loan_is_404(today, clerk_client) -> None:
    assert clerk_client.post("/odunc/999/uzat/").status_code == 404


# --- Check-in screen (FR-09, FR-12) ----------------------------------------------


def test_checkin_screen_focuses_the_barcode(clerk_client) -> None:
    body = _body(clerk_client.get("/iade/"))
    assert _autofocused(body) == ["nusha"]
    assert 'method="post"' in body


def test_tc135_late_return_writes_a_fine(today, clerk_client, member) -> None:
    loan = make_loan(member, due_on=date(2026, 11, 16))
    today(date(2026, 11, 19))
    response = clerk_client.post("/iade/", {"nusha": loan.copy.barcode})
    assert response.status_code == 303
    assert response["Location"] == "/iade/"
    body = _body(clerk_client.get("/iade/"))
    assert "İade alındı; 15,00 TL ceza yazıldı" in body
    assert _autofocused(body) == ["nusha"]
    loan.refresh_from_db()
    assert not loan.is_open and loan.copy.status == CopyStatus.ON_SHELF
    fine = LedgerEntry.objects.get()
    assert (fine.amount_kurus, fine.loan, fine.member) == (1500, loan, member)


def test_on_time_return_message(today, clerk_client, member) -> None:
    loan = make_loan(member, due_on=date(2026, 11, 16))
    clerk_client.post("/iade/", {"nusha": loan.copy.barcode})
    body = _body(clerk_client.get("/iade/"))
    assert "İade alındı" in body and "ceza" not in body


def test_tc283_closed_date_is_not_fined(today, clerk_client, member) -> None:
    ClosedDate.objects.create(date=date(2026, 11, 18))
    loan = make_loan(member, due_on=date(2026, 11, 16))
    today(date(2026, 11, 20))
    clerk_client.post("/iade/", {"nusha": loan.copy.barcode})
    assert "İade alındı; 15,00 TL ceza yazıldı" in _body(clerk_client.get("/iade/"))


def test_checkin_refusal_reshows_with_200(today, clerk_client) -> None:
    copy = make_copy(pk=42)
    response = clerk_client.post("/iade/", {"nusha": copy.barcode})
    assert response.status_code == 200
    assert "Bu nüshanın açık ödüncü yok" in _body(response)


def test_checkin_search_lists_loaned_copies(today, clerk_client, member) -> None:
    book = make_book("İnce Memed", "Yaşar Kemal")
    loan = make_loan(member, make_copy(book, pk=42))
    make_copy(book, pk=43)
    response = clerk_client.post("/iade/", {"nusha": "memed"})
    assert response.status_code == 200
    body = _body(response)
    assert f'name="nusha" value="{loan.copy.barcode}"' in body and "İade al" in body
    assert 'value="00000043"' not in body
    assert "Nüsha bulunamadı" in _body(clerk_client.post("/iade/", {"nusha": "yok"}))


def test_scan_js_is_served_as_a_static_file() -> None:
    from django.contrib.staticfiles import finders

    path = finders.find("js/scan.js")
    assert path is not None
    source = open(path, encoding="utf-8").read()
    assert "data-next-focus" in source and "autofocus" in source
