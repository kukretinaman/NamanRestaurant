from django import template
register = template.Library()

@register.filter
def dict_get(d, key):
    if d is None:
        return None
    return d.get(key, None)
