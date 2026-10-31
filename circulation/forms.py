"""Copy status forms (G12). Amounts are entered in TL and kept in kuruş (KL-3)."""

from __future__ import annotations

from django import forms

from administration.forms import TLField

NOTE_MAX = 500


class CopyMarkForm(forms.Form):
    """Lost or damaged; ``fee`` is used only for a copy on loan (KL-7)."""

    fee = TLField(label="Bedel (TL)", required=False)
    note = forms.CharField(label="Not", max_length=NOTE_MAX, required=False)


class NoteForm(forms.Form):
    note = forms.CharField(label="Not", max_length=NOTE_MAX, required=False)
