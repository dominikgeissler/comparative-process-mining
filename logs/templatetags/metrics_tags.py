from typing import List
from django import template


register = template.Library()

@register.filter
def is_list(obj):
    return isinstance(obj, List)

@register.filter
def key_resolve(key):
    if key == "no_cases":
        ret = "Number of Cases"
    elif key == "no_events":
        ret = "Number of Events"
    elif key == "no_variants":
        ret = "Number of Variants"
    elif key == "no_attributes":
        ret = "Number of Attributes"
    elif key == "avg_case_duration":
        ret = "Average Case Duration"
    elif key == "median_case_duration":
        ret = "Median Case Duration"
    elif key == "total_case_duration":
        ret = "Total Case Duration"
    else:
        ret = key
    return ret