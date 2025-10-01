from django import template
import re

register = template.Library()

@register.filter
def limpar_telefone(value):
    if not value:
        return ''
    return re.sub(r'[^0-9]', '', value)
