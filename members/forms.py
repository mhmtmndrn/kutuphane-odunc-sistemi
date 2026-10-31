"""Member forms (plan G06). Rules live in the services; forms check shape."""

from __future__ import annotations

from django import forms

DATE_FORMATS = ["%Y-%m-%d", "%d.%m.%Y"]


class MemberForm(forms.Form):
    full_name = forms.CharField(label="Ad soyad", max_length=200)
    phone = forms.CharField(label="Telefon", max_length=30)
    email = forms.EmailField(label="E-posta", max_length=254, required=False)


class ConsentForm(forms.Form):
    """``given`` is "1" (give) or "0" (withdraw); ``on`` defaults to today."""

    given = forms.TypedChoiceField(
        choices=[("1", "Rıza ver"), ("0", "Rızayı geri al")],
        coerce=lambda value: value == "1",
        widget=forms.HiddenInput,
    )
    on = forms.DateField(
        label="Tarih",
        input_formats=DATE_FORMATS,
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
