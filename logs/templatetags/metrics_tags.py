from typing import List
from django import template


register = template.Library()


@register.filter
def is_list(obj):
    """determines whether an object is a list or not"""
    return isinstance(obj, List)


@register.filter
def key_resolve(metric):
    """internal variable to readable text"""
    # if the metric is a "Number of..."
    if metric.split("_")[0] == "no":
        # replace "no" with "Number of" and capitalize the other word
        return "Number of " + metric.split("_")[1].capitalize()
    else:
        # split the name by the '_' and capitalize each word
        return " ".join(metric.split("_")).title()
