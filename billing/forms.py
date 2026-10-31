"""Ledger forms. Amounts are entered in TL and kept in kuruş (KL-3)."""

from __future__ import annotations

from django import forms

from administration.forms import TLField

REASON_MAX = 500  # data-design §2.5


class PaymentForm(forms.Form):
    amount = TLField(label="Tutar (TL)")


class WaiverForm(forms.Form):
    # The id is checked by the service (``get_entry``), not by the choice
    # list, so a stale page gets the service's message.
    charge_id = forms.IntegerField(label="Kalem", widget=forms.Select)
    amount = TLField(label="Tutar (TL)")
    reason = forms.CharField(label="Gerekçe", max_length=REASON_MAX, required=False, strip=False)

    def __init__(self, *args, charges=(), **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["charge_id"].widget.choices = list(charges)


class RefundForm(forms.Form):
    fee_id = forms.IntegerField(widget=forms.HiddenInput)
    amount = TLField(label="Tutar (TL)")


class CancelForm(forms.Form):
    fee_id = forms.IntegerField(widget=forms.HiddenInput)
    reason = forms.CharField(label="Gerekçe", max_length=REASON_MAX, required=False, strip=False)
