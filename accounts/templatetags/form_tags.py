'''
File: form_tags.py
Author: Beveridge Ekpolomo
Description: Custom template filters for form handling and styling.
Part of the User Authentication & Profiles module for the University Dashboard application.
Adapted from Sky Health Check project.
'''

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
