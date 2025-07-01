from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        value = dictionary.get(key)
        if isinstance(value, dict):
            return value
    return None