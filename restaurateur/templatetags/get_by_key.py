from django import template

register = template.Library()


@register.filter
def get_by_key(d, key):
    return d[key]
