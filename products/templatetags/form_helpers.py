# form_helpers.py

from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    try:
        return form[field_name]
    except KeyError:
        return None

@register.filter(name='split')
def split(value, key):
    return value.split(key)