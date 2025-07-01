from django import template
register = template.Library()

@register.filter
def dict_get(dict_list, key):
    for k, v in dict_list:
        if k == key:
            return v
    return key