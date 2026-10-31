"""View tests for members (G06).

TC-57 and TC-58 (consent dates on the member page), TC-259, TC-260 (detail
part); plus the search, create, edit, consent and reactivation screens.
"""

from __future__ import annotations

from datetime import date

import pytest
from django.test import Client

from accounts.models import Role
from administration import clock
from administration.audit import AuditAction
from administration.models import AuditEvent
from members import services
from members.models import ConsentEvent, Member
from tests.support.factories import make_member, make_staff

pytestmark = pytest.mark.django_db


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK)


@pytest.fixture
def clerk_client(client: Client, clerk) -> Client:
    client.force_login(clerk)
    return client


@pytest.fixture
def today(monkeypatch: pytest.MonkeyPatch):
    def set_today(day: date) -> None:
        monkeypatch.setattr(clock, "today", lambda: day)

    set_today(date(2026, 11, 1))
    return set_today


def _reactivate_form(member_no: int) -> str:
    return f'action="/uyeler/{member_no}/aktif/"'


# --- Search -------------------------------------------------------------------


def test_search_page_without_query_shows_the_form(clerk_client) -> None:
    response = clerk_client.get("/uyeler/")
    assert response.status_code == 200
    assert 'name="q"' in response.content.decode()
    assert "Sonuç yok." not in response.content.decode()


def test_search_lists_matches_with_links(clerk_client) -> None:
    make_member("Ayşe Yılmaz", "0555 111 22 33", member_no=1042)
    make_member("Mehmet Demir", "0532 000 00 00", member_no=1043)
    response = clerk_client.get("/uyeler/", {"q": "AYŞE"})
    html = response.content.decode()
    assert response.status_code == 200
    assert 'href="/uyeler/1042/"' in html
    assert "Ayşe Yılmaz" in html
    assert "Mehmet Demir" not in html


def test_search_without_matches_says_so(clerk_client) -> None:
    response = clerk_client.get("/uyeler/", {"q": "zzz"})
    assert "Sonuç yok." in response.content.decode()


def test_search_shows_inactive_status(clerk_client) -> None:
    make_member("Ayşe Yılmaz", is_active=False)
    assert "Pasif" in clerk_client.get("/uyeler/", {"q": "ayse"}).content.decode()


def test_member_pages_need_login(client: Client) -> None:
    response = client.get("/uyeler/")
    assert response.status_code == 302
    assert response["Location"].startswith("/giris/")


# --- Create and edit ----------------------------------------------------------


def test_create_member_redirects_to_the_detail(clerk_client) -> None:
    assert clerk_client.get("/uyeler/yeni/").status_code == 200
    response = clerk_client.post(
        "/uyeler/yeni/",
        {"full_name": "Ayşe Yılmaz", "phone": "0555 111 22 33", "email": ""},
    )
    member = Member.objects.get()
    assert response.status_code == 302
    assert response["Location"] == f"/uyeler/{member.member_no}/"
    assert member.email is None
    follow = clerk_client.get(response["Location"])
    assert "Üye kaydedildi" in follow.content.decode()


def test_create_member_rule_violation_reshows_the_form(clerk_client) -> None:
    response = clerk_client.post("/uyeler/yeni/", {"full_name": "Ayşe", "phone": "yok"})
    assert response.status_code == 200
    assert "Telefon 1 ile 20 rakam içermeli" in response.content.decode()
    assert Member.objects.count() == 0


def test_create_member_form_errors_reshow_the_form(clerk_client) -> None:
    response = clerk_client.post("/uyeler/yeni/", {"full_name": "", "phone": "0555"})
    assert response.status_code == 200
    assert Member.objects.count() == 0


def test_edit_member(clerk_client) -> None:
    member = make_member(member_no=7)
    response = clerk_client.get("/uyeler/7/duzenle/")
    assert response.status_code == 200
    assert "Ayşe Yılmaz" in response.content.decode()
    response = clerk_client.post(
        "/uyeler/7/duzenle/",
        {"full_name": "Ayşe Demir", "phone": "0555 111 22 33", "email": "ayse@example.org"},
    )
    assert response.status_code == 302
    assert response["Location"] == "/uyeler/7/"
    member.refresh_from_db()
    assert (member.full_name, member.email) == ("Ayşe Demir", "ayse@example.org")


def test_edit_member_rule_violation_reshows_the_form(clerk_client) -> None:
    make_member(member_no=7)
    response = clerk_client.post("/uyeler/7/duzenle/", {"full_name": "Ayşe", "phone": "yok"})
    assert response.status_code == 200
    assert "Telefon 1 ile 20 rakam içermeli" in response.content.decode()


def test_edit_anonymized_member_is_refused_with_200(clerk_client) -> None:
    make_member(member_no=7, anonymized=True)
    response = clerk_client.post(
        "/uyeler/7/duzenle/", {"full_name": "Ayşe", "phone": "0555", "email": ""}
    )
    assert response.status_code == 200
    assert "Anonimleştirilmiş üye güncellenemez" in response.content.decode()
    assert Member.objects.get().full_name is None


def test_unknown_member_is_404(clerk_client) -> None:
    assert clerk_client.get("/uyeler/99/").status_code == 404
    assert clerk_client.get("/uyeler/99/duzenle/").status_code == 404
    assert clerk_client.post("/uyeler/99/aktif/").status_code == 404
    assert clerk_client.post("/uyeler/99/riza/", {"given": "1"}).status_code == 404


# --- Detail and consent (TC-57, TC-58) ----------------------------------------


def test_tc57_member_page_shows_both_consent_dates(clerk_client, clerk, today) -> None:
    member = make_member(member_no=5, email="ayse@example.org")
    response = clerk_client.post("/uyeler/5/riza/", {"given": "1", "on": "2026-11-01"})
    assert response.status_code == 302
    assert response["Location"] == "/uyeler/5/"
    today(date(2026, 12, 1))
    clerk_client.post("/uyeler/5/riza/", {"given": "0", "on": "01.12.2026"})
    member.refresh_from_db()
    assert not member.has_email_consent
    html = clerk_client.get("/uyeler/5/").content.decode()
    assert "01.11.2026" in html
    assert "01.12.2026" in html


def test_tc58_member_page_shows_the_latest_dates(clerk_client, clerk, today) -> None:
    member = make_member(member_no=5, email="ayse@example.org")
    today(date(2026, 12, 20))
    services.set_consent(clerk, member, True, date(2026, 11, 1))
    services.set_consent(clerk, member, False, date(2026, 12, 1))
    services.set_consent(clerk, member, True, date(2026, 12, 15))
    html = clerk_client.get("/uyeler/5/").content.decode()
    assert "15.12.2026" in html
    assert "01.12.2026" in html
    assert "01.11.2026" not in html


def test_consent_rule_violation_reshows_the_detail_with_200(clerk_client, today) -> None:
    make_member(member_no=5, email="ayse@example.org")
    response = clerk_client.post("/uyeler/5/riza/", {"given": "1", "on": "2026-11-05"})
    assert response.status_code == 200
    assert "Rıza tarihi gelecekte olamaz" in response.content.decode()
    assert ConsentEvent.objects.count() == 0


def test_consent_form_error_reshows_the_detail(clerk_client, today) -> None:
    make_member(member_no=5, email="ayse@example.org")
    response = clerk_client.post("/uyeler/5/riza/", {"given": "1", "on": "dün"})
    assert response.status_code == 200
    assert ConsentEvent.objects.count() == 0


def test_consent_date_defaults_to_today(clerk_client, today) -> None:
    make_member(member_no=5, email="ayse@example.org")
    html = clerk_client.get("/uyeler/5/").content.decode()
    assert 'value="2026-11-01"' in html


def test_member_without_email_gets_no_consent_button(clerk_client) -> None:
    make_member(member_no=5, email=None)
    html = clerk_client.get("/uyeler/5/").content.decode()
    assert 'action="/uyeler/5/riza/"' not in html
    assert "Rıza için e-posta adresi gerekli" in html


def test_detail_shows_member_fields(clerk_client) -> None:
    make_member("Ayşe Yılmaz", "0555 111 22 33", "ayse@example.org", member_no=5)
    html = clerk_client.get("/uyeler/5/").content.decode()
    for text in ("Ayşe Yılmaz", "0555 111 22 33", "ayse@example.org", 'href="/uyeler/5/duzenle/"'):
        assert text in html


# --- Reactivation (TC-259, TC-260) --------------------------------------------


def test_tc259_clerk_reactivates_member_from_the_detail_page(clerk_client, clerk) -> None:
    member = make_member(member_no=42, is_active=False, deactivated_on=date(2026, 10, 1))
    html = clerk_client.get("/uyeler/42/").content.decode()
    assert _reactivate_form(42) in html
    assert "Aktifleştir</button>" in html
    response = clerk_client.post("/uyeler/42/aktif/")
    assert response.status_code == 302
    assert response["Location"] == "/uyeler/42/"
    member.refresh_from_db()
    assert member.is_active
    assert member.deactivated_on is None
    event = AuditEvent.objects.get()
    assert event.action == AuditAction.MEMBER_REACTIVATED
    assert (event.actor, event.target_type, event.target_id) == (clerk, "member", member.pk)
    assert event.details == {"member_no": 42}


@pytest.mark.parametrize("kwargs", [{"is_active": True}, {"anonymized": True}])
def test_tc260_no_reactivate_button_for_active_or_anonymized(clerk_client, kwargs) -> None:
    make_member(member_no=42, **kwargs)
    html = clerk_client.get("/uyeler/42/").content.decode()
    assert _reactivate_form(42) not in html
    assert "Aktifleştir</button>" not in html


def test_reactivating_an_active_member_reshows_the_detail_with_200(clerk_client) -> None:
    make_member(member_no=42)
    response = clerk_client.post("/uyeler/42/aktif/")
    assert response.status_code == 200
    assert "Üye zaten aktif" in response.content.decode()
    assert AuditEvent.objects.count() == 0


def test_anonymized_detail_has_no_edit_link_or_consent_form(clerk_client) -> None:
    make_member(member_no=42, anonymized=True)
    html = clerk_client.get("/uyeler/42/").content.decode()
    assert "Anonimleştirilmiş üye" in html
    assert 'href="/uyeler/42/duzenle/"' not in html
    assert 'action="/uyeler/42/riza/"' not in html


def test_reactivate_and_consent_are_post_only(clerk_client) -> None:
    make_member(member_no=42, is_active=False)
    assert clerk_client.get("/uyeler/42/aktif/").status_code == 405
    assert clerk_client.get("/uyeler/42/riza/").status_code == 405


def test_home_links_to_members(clerk_client) -> None:
    assert 'href="/uyeler/"' in clerk_client.get("/").content.decode()


# --- Member cards (G08: TC-269) -------------------------------------------------


def test_tc269_card_range_form(clerk_client) -> None:
    response = clerk_client.get("/uyeler/kart/")
    html = response.content.decode()
    assert response.status_code == 200
    assert 'name="start"' in html and 'name="end"' in html


def test_tc269_card_pdf_from_a_range_and_from_checkboxes(clerk_client) -> None:
    make_member(member_no=1)
    make_member(member_no=2)
    for data in ({"start": "1", "end": "2"}, {"member_nos": ["2", "1"]}):
        response = clerk_client.post("/uyeler/kart/", data)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert response["Content-Disposition"] == 'inline; filename="uye-kartlari.pdf"'
        assert response.content.startswith(b"%PDF")


def test_tc269_inactive_member_has_no_checkbox_in_search_results(clerk_client) -> None:
    make_member("Ayşe Yılmaz", member_no=1)
    make_member("Ayşe Demir", member_no=2, is_active=False)
    make_member(member_no=3, anonymized=True)
    html = clerk_client.get("/uyeler/", {"q": "ayse"}).content.decode()
    assert 'name="member_nos" value="1"' in html
    assert 'name="member_nos" value="2"' not in html
    assert 'action="/uyeler/kart/"' in html
    assert "Kart bas</button>" in html
    html = clerk_client.get("/uyeler/", {"q": "3"}).content.decode()
    assert 'name="member_nos" value="3"' not in html


def test_card_selection_error_reshows_the_range_form_with_200(clerk_client) -> None:
    response = clerk_client.post("/uyeler/kart/", {"start": "5", "end": "1"})
    assert response.status_code == 200
    assert "Başlangıç bitişten büyük olamaz" in response.content.decode()


def test_card_form_rejects_non_numbers(clerk_client) -> None:
    response = clerk_client.post("/uyeler/kart/", {"start": "a", "end": "2"})
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/html")
    response = clerk_client.post("/uyeler/kart/", {"member_nos": ["x"]})
    assert "Geçersiz seçim" in response.content.decode()


def test_no_card_button_when_no_result_is_printable(clerk_client) -> None:
    make_member("Ayşe Demir", member_no=2, is_active=False)
    html = clerk_client.get("/uyeler/", {"q": "ayse"}).content.decode()
    assert "Kart bas</button>" not in html
