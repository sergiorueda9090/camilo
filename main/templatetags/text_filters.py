import html
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def decode_entities(value):
    """Decodifica entidades HTML a caracteres reales (ej: &oacute; → ó)"""
    if not value:
        return value
    return html.unescape(str(value))
