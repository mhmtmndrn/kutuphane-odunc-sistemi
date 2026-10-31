"""Billing view tests (G09): TC-86, TC-91, TC-97…TC-99, TC-275; plus the
payment, waiver, refund and cancellation forms."""

from __future__ import annotations

import re
from datetime import date

import pytest
from django.test import Client
from django.utils import timezone

from accounts.models import Role
from administration.models import AuditEvent
from billing import services
from billing.models import EntryKind, LedgerEntry
from circulation.models import CloseReason
from tests.support.factories import make_charge, make_loan, make_member, make_staff

pytestmark = pytest.mark.django_db


@pytest.fixture
def clerk():
    return make_staff("ali", role=Role.CLERK, full_name="Ali Yılmaz")


@pytest.fixture
def admin():
    return make_staff("ayse.y", role=Role.ADMIN, full_name="Ayşe Yıldız")


@pytest.fixture
def clerk_client(client: Client, clerk) -> Client:
    client.force_login(clerk)
    return client


@pytest.fixture
def admin_client(client: Client, admin) -> Client:
    client.force_login(admin)
    return client


@pytest.fixture
def member():
    return make_member("Mehmet Demir", member_no=1042)


def _body(response) -> str:
    return response.content.decode()


def _forms(body: str, action: str) -> list[str]:
    """The HTML of every form posting to ``action``."""
    return re.findall(rf'<form[^>]*action="{re.escape(action)}".*?</form>', body, re.S)


def _fee_ids(body: str, action: str) -> set[int]:
    ids = set()
    for form in _forms(body, action):
        ids.update(int(v) for v in re.findall(r'name="fee_id" value="(\d+)"', form))
    return ids


def _found_lost_fee(member, amount: int = 12000) -> LedgerEntry:
    loan = make_loan(
        member,
        closed_on=date(2026, 11, 20),
        close_reason=CloseReason.LOST,
        copy_found_on=date(2026, 11, 25),
    )
    return make_charge(member, EntryKind.FEE, amount, loan=loan)


# --- Statement (FR-17) ---------------------------------------------------------


def test_tc98_statement_shows_balance_and_entries(clerk_client, clerk, admin, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    services.record_payment(clerk, member, 500)
    services.waive(admin, fine, 500, "Hastalık")
    response = clerk_client.get("/borclar/1042/")
    assert response.status_code == 200
    body = _body(response)
    assert "Güncel borç: 5,00 TL" in body
    rows = response.context["rows"]
    assert [r.kind_label for r in rows] == ["Ceza", "Ödeme", "Af"]
    for label in ("Ceza", "Ödeme", "Af", "15,00 TL", "Hastalık", "Ali Yılmaz", "Ayşe Yıldız"):
        assert label in body
    today = timezone.localtime(rows[0].created_at).strftime("%d.%m.%Y")
    assert body.count(today) >= 3


def test_tc99_cancellation_and_refund_rows(clerk_client, clerk, admin, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 2000)
    services.cancel_unpaid(clerk, fee)
    services.refund(admin, fee, 2000)
    response = clerk_client.get("/borclar/1042/")
    body = _body(response)
    assert "İptal" in body and "Para iadesi" in body
    assert "Güncel borç: 0,00 TL" in body


def test_statement_unknown_member_is_404(clerk_client) -> None:
    assert clerk_client.get("/borclar/999/").status_code == 404


def test_statement_links_back_to_the_member(clerk_client, member) -> None:
    assert 'href="/uyeler/1042/"' in _body(clerk_client.get("/borclar/1042/"))


# --- Payment (FR-13) -----------------------------------------------------------


def test_payment_form_records_and_redirects(clerk_client, member) -> None:
    make_charge(member, EntryKind.FINE, 4000)
    response = clerk_client.post("/borclar/1042/odeme/", {"amount": "15,00"})
    assert response.status_code == 302
    assert response["Location"] == "/borclar/1042/"
    assert services.member_balance(member) == 2500
    follow = clerk_client.get("/borclar/1042/")
    assert "Ödeme alındı: 15,00 TL" in _body(follow)


def test_payment_above_debt_reshows_the_page_with_200(clerk_client, member) -> None:
    make_charge(member, EntryKind.FINE, 4000)
    response = clerk_client.post("/borclar/1042/odeme/", {"amount": "40,01"})
    assert response.status_code == 200
    assert "Ödeme tutarı borcu aşamaz" in _body(response)
    assert services.member_balance(member) == 4000


def test_payment_with_bad_amount_is_a_form_error(clerk_client, member) -> None:
    make_charge(member, EntryKind.FINE, 4000)
    response = clerk_client.post("/borclar/1042/odeme/", {"amount": "abc"})
    assert response.status_code == 200
    assert "Geçerli bir tutar girin (ör. 5,00)" in _body(response)
    assert not LedgerEntry.objects.filter(kind="PAYMENT").exists()


def test_payment_form_only_with_debt(clerk_client, member) -> None:
    assert not _forms(_body(clerk_client.get("/borclar/1042/")), "/borclar/1042/odeme/")
    make_charge(member, EntryKind.FINE, 100)
    assert _forms(_body(clerk_client.get("/borclar/1042/")), "/borclar/1042/odeme/")


# --- Waiver (FR-14, FR-26) -----------------------------------------------------


def test_tc86_clerk_cannot_waive(clerk_client, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    response = clerk_client.post(
        "/borclar/1042/af/", {"charge_id": fine.id, "amount": "5,00", "reason": "Hastalık"}
    )
    assert response.status_code == 403
    assert not LedgerEntry.objects.filter(kind="WAIVER").exists()
    assert not _forms(_body(clerk_client.get("/borclar/1042/")), "/borclar/1042/af/")


def test_tc91_waiver_shows_on_the_audit_list(admin_client, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    response = admin_client.post(
        "/borclar/1042/af/", {"charge_id": fine.id, "amount": "5,00", "reason": "Hastalık"}
    )
    assert response.status_code == 302
    event = AuditEvent.objects.get(action="WAIVER")
    body = _body(admin_client.get("/denetim/"))
    row = re.search(r"<tr>(?:(?!</tr>).)*Af(?:(?!</tr>).)*</tr>", body, re.S)
    assert row is not None
    row_html = row.group(0)
    for text in ("Af", "5,00 TL", "Hastalık", "ayse.y"):
        assert text in row_html
    local = timezone.localtime(event.occurred_at)
    assert local.strftime("%d.%m.%Y %H:%M") in row_html


def test_waiver_rule_violation_reshows_with_200(admin_client, member) -> None:
    fine = make_charge(member, EntryKind.FINE, 1500)
    response = admin_client.post(
        "/borclar/1042/af/", {"charge_id": fine.id, "amount": "5,00", "reason": "  "}
    )
    assert response.status_code == 200
    assert "Af için gerekçe zorunlu" in _body(response)


def test_waiver_of_another_members_entry_is_refused(admin_client, member) -> None:
    other = make_member("Başka Üye", member_no=7)
    fine = make_charge(other, EntryKind.FINE, 1500)
    response = admin_client.post(
        "/borclar/1042/af/", {"charge_id": fine.id, "amount": "5,00", "reason": "Hastalık"}
    )
    assert response.status_code == 200
    assert "Kalem bulunamadı" in _body(response)
    assert not LedgerEntry.objects.filter(kind="WAIVER").exists()


def test_waiver_form_lists_open_charges_only(admin_client, clerk, member) -> None:
    paid = make_charge(member, EntryKind.FINE, 500)
    open_fine = make_charge(member, EntryKind.FINE, 1500)
    services.record_payment(clerk, member, 500)
    form = _forms(_body(admin_client.get("/borclar/1042/")), "/borclar/1042/af/")[0]
    values = {int(v) for v in re.findall(r'<option value="(\d+)"', form)}
    assert values == {open_fine.id}
    assert paid.id not in values


# --- Refund and manual cancellation (FR-16, ADR-0037, ADR-0041) ----------------


def test_tc97_clerk_cannot_refund(clerk_client, clerk, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 2000)
    response = clerk_client.post("/borclar/1042/para-iadesi/", {"fee_id": fee.id, "amount": "5,00"})
    assert response.status_code == 403
    assert not LedgerEntry.objects.filter(kind="REFUND").exists()


def test_refund_form_records_and_redirects(admin_client, clerk, member) -> None:
    fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 2000)
    response = admin_client.post(
        "/borclar/1042/para-iadesi/", {"fee_id": fee.id, "amount": "20,00"}
    )
    assert response.status_code == 302
    assert services.refundable(fee) == 0
    response = admin_client.post(
        "/borclar/1042/para-iadesi/", {"fee_id": fee.id, "amount": "1,00"}
    )
    assert response.status_code == 200
    assert "Para iadesi, ödenmiş ve henüz iade edilmemiş tutarı aşamaz" in _body(response)


def test_tc275_admin_forms_follow_the_fee_state(client, clerk, admin, member) -> None:
    refundable_fee = _found_lost_fee(member)
    services.record_payment(clerk, member, 2000)
    unlinked = make_charge(member, EntryKind.FEE, 5000)
    neither = make_charge(member, EntryKind.FEE, 3000, loan=make_loan(member))

    client.force_login(clerk)
    response = client.post("/borclar/1042/iptal/", {"fee_id": unlinked.id, "reason": "Bulundu"})
    assert response.status_code == 403
    clerk_body = _body(client.get("/borclar/1042/"))
    assert not _forms(clerk_body, "/borclar/1042/para-iadesi/")
    assert not _forms(clerk_body, "/borclar/1042/iptal/")

    client.force_login(admin)
    admin_body = _body(client.get("/borclar/1042/"))
    assert _fee_ids(admin_body, "/borclar/1042/para-iadesi/") == {refundable_fee.id}
    assert _fee_ids(admin_body, "/borclar/1042/iptal/") == {unlinked.id}
    assert neither.id not in _fee_ids(admin_body, "/borclar/1042/para-iadesi/")


def test_manual_cancellation_form(admin_client, member) -> None:
    fee = make_charge(member, EntryKind.FEE, 5000)
    response = admin_client.post("/borclar/1042/iptal/", {"fee_id": fee.id, "reason": ""})
    assert response.status_code == 200
    assert "İptal için gerekçe zorunlu" in _body(response)
    response = admin_client.post(
        "/borclar/1042/iptal/", {"fee_id": fee.id, "reason": "Nüsha bulundu"}
    )
    assert response.status_code == 302
    assert services.member_balance(member) == 0


def test_post_only_routes_refuse_get(admin_client, member) -> None:
    for url in ("/borclar/1042/odeme/", "/borclar/1042/af/", "/borclar/1042/para-iadesi/"):
        assert admin_client.get(url).status_code == 405
