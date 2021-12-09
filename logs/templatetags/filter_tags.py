from django import template
from pandas import Timestamp
from datetime import datetime

register = template.Library()
formatstring = "%Y-%m-%d %H:%M:%S"

@register.filter
def convert_timestamp(timestamp):
    if type(timestamp) is Timestamp or type(timestamp) is datetime:
        return timestamp.strftime(formatstring)
    else:
        return timestamp

@register.filter
def get_attributes(log):
    import json
    return json.dumps(list(log.get_properties().keys()))

@register.filter
def get_operations(attribute_list):
    import numbers
    for attribute in attribute_list:
        if isinstance(attribute, numbers.Number):
            continue
        else:
            return ['=', '≠']
    return ['<', '>', '=', '≠']