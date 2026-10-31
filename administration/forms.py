"""Administration forms. Amounts are entered in TL and kept in kuruş (KL-3)."""

from __future__ import annotations

from django import forms

from .models import LibrarySettings
from .money import format_tl, parse_tl

WEEKDAYS = [
    (0, "Pazartesi"),
    (1, "Salı"),
    (2, "Çarşamba"),
    (3, "Perşembe"),
    (4, "Cuma"),
    (5, "Cumartesi"),
    (6, "Pazar"),
]


class TLField(forms.CharField):
    """A Turkish lira amount such as "1.250,50"; cleans to integer kuruş."""

    widget = forms.TextInput(attrs={"inputmode": "decimal", "maxlength": 20})

    def to_python(self, value):
        value = super().to_python(value)
        if value in self.empty_values:
            return None
        try:
            return parse_tl(value)
        except ValueError:
            raise forms.ValidationError("Geçerli bir tutar girin (ör. 5,00)") from None

    def prepare_value(self, value):
        if isinstance(value, int):
            return format_tl(value).removesuffix(" TL")
        return value


class SettingsForm(forms.Form):
    loan_period_days = forms.IntegerField(label="Ödünç süresi (gün)", min_value=1, max_value=365)
    max_open_loans = forms.IntegerField(label="Aynı anda ödünç limiti", min_value=1, max_value=20)
    daily_fine = TLField(label="Günlük ceza (TL)")
    fine_cap = TLField(label="Ödünç başına ceza üst sınırı (TL)")
    debt_threshold = TLField(label="Borç eşiği (TL)")
    retention_years = forms.IntegerField(label="Saklama süresi (yıl)", min_value=1, max_value=10)
    library_name = forms.CharField(label="Kütüphane adı", max_length=80)

    # Form field -> LibrarySettings field.
    FIELD_MAP = {
        "loan_period_days": "loan_period_days",
        "max_open_loans": "max_open_loans",
        "daily_fine": "daily_fine_kurus",
        "fine_cap": "fine_cap_kurus",
        "debt_threshold": "debt_threshold_kurus",
        "retention_years": "retention_years",
        "library_name": "library_name",
    }

    @classmethod
    def initial_from(cls, settings: LibrarySettings) -> dict[str, object]:
        return {name: getattr(settings, model) for name, model in cls.FIELD_MAP.items()}

    def changes(self) -> dict[str, object]:
        return {model: self.cleaned_data[name] for name, model in self.FIELD_MAP.items()}


class WeeklyClosedForm(forms.Form):
    weekdays = forms.TypedMultipleChoiceField(
        label="Haftalık kapalı günler",
        choices=WEEKDAYS,
        coerce=int,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )


class ClosedDateForm(forms.Form):
    date = forms.DateField(
        label="Tarih",
        input_formats=["%Y-%m-%d", "%d.%m.%Y"],
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
    )
    note = forms.CharField(label="Not", max_length=200, required=False)
