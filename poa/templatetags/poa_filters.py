from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Filtro personalizado para acceder a elementos de diccionarios en templates"""
    if dictionary is None:
        return None
    return dictionary.get(key)
