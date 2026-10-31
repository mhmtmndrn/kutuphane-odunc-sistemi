"""``{{ event.details|details_text }}``: audit details as readable JSON."""

import json

from django import template

register = template.Library()


@register.filter
def details_text(details: dict) -> str:
    return json.dumps(details, ensure_ascii=False, sort_keys=True)
