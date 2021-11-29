from typing import List
from django import template


register = template.Library()

@register.filter
def is_list(obj):
    return isinstance(obj, List)