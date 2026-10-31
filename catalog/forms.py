"""Book and copy forms (plan G07)."""

from __future__ import annotations

from django import forms

from administration.forms import IntListField

from .domain import CHECK_REASON, IsbnOk, IsbnSuggest, parse_isbn
from .services import COPIES_MAX, COPIES_MIN, suggestion_message


class BookForm(forms.Form):
    """Validates the ISBN with ``parse_isbn`` (ADR-0008).

    An ``IsbnSuggest`` result keeps the form invalid and sets ``suggestion``;
    the template then shows a second submit button ``name="isbn_accept"``
    carrying the suggested value. That value is parsed again and saved only
    if it is ``IsbnOk``.
    """

    title = forms.CharField(label="Başlık", max_length=300)
    author = forms.CharField(label="Yazar", max_length=300)
    isbn = forms.CharField(label="ISBN", max_length=40, required=False)
    publisher = forms.CharField(label="Yayınevi", max_length=200, required=False)
    year = forms.IntegerField(label="Yıl", min_value=1, max_value=9999, required=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.suggestion: str | None = None

    def clean_isbn(self) -> str | None:
        accepted = self.data.get("isbn_accept", "").strip()
        raw = accepted or self.cleaned_data["isbn"].strip()
        if not raw:
            return None
        result = parse_isbn(raw)
        if isinstance(result, IsbnOk):
            return result.isbn13
        if isinstance(result, IsbnSuggest) and not accepted:
            self.suggestion = result.suggestion
            raise forms.ValidationError(suggestion_message(result.suggestion))
        # A tampered ``isbn_accept`` that only earns a suggestion is refused.
        reason = CHECK_REASON if isinstance(result, IsbnSuggest) else result.reason
        raise forms.ValidationError(reason)


class AddCopiesForm(forms.Form):
    # The 1–50 range is checked by ``add_copies`` (KL-19), whose message the
    # screen shows; the widget only hints it to the browser.
    count = forms.IntegerField(
        label="Nüsha sayısı",
        initial=1,
        widget=forms.NumberInput(attrs={"min": COPIES_MIN, "max": COPIES_MAX}),
    )


class LabelSelectionForm(forms.Form):
    """A barcode range or the ``copy_ids`` checkboxes (ADR-0036); the rules
    are in ``copies_for_labels``."""

    start = forms.CharField(label="Başlangıç barkodu", max_length=20, required=False)
    end = forms.CharField(label="Bitiş barkodu", max_length=20, required=False)
    copy_ids = IntListField()
