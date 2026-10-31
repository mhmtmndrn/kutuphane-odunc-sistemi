"""``{{ event.details|details_text }}``: audit details as readable JSON.

Money keys are shown in TL ("5,00 TL") instead of kuruş (plan §11, G09);
the stored JSON is unchanged.
"""

import json

from django import template

from administration.money import format_tl

register = template.Library()

MONEY_KEYS = frozenset({"amount_kurus", "fee_kurus"})


@register.filter
def details_text(details: dict) -> str:
    shown = {
        key: format_tl(value) if key in MONEY_KEYS and isinstance(value, int) else value
        for key, value in details.items()
    }
    return json.dumps(shown, ensure_ascii=False, sort_keys=True)
