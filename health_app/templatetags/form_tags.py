from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """Add a CSS class to a form field."""
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='split')
def split(value, delimiter):
    """Split a string into a list using the given delimiter."""
    return value.split(delimiter)
