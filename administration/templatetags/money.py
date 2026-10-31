"""Template filter ``tl``: ``{{ amount_kurus|tl }}`` → "1.250,00 TL" (KL-3)."""

from django import template

from administration.money import format_tl

register = template.Library()


@register.filter(name="tl")
def tl(kurus: int) -> str:
    return format_tl(kurus)
