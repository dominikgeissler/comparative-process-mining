from typing import List
from django import template


register = template.Library()


@register.filter
def is_list(obj):
    return isinstance(obj, List)


@register.filter
def key_resolve(metric):
    if metric.split("_")[0] == "no":
        return "Number of " + metric.split("_")[1].capitalize()
    else:
        return " ".join(metric.split("_")).title()
