from django import template
from pandas import Timestamp
from datetime import datetime
from numbers import Number
from json import dumps

register = template.Library()
formatstring = "%Y-%m-%d %H:%M:%S"

@register.filter
def convert_timestamp(timestamp):
    """converts the timestamp to a format django can handle"""
    if type(timestamp) is Timestamp or type(timestamp) is datetime:
        # timestamp is not formatted yet
        return timestamp.strftime(formatstring)
    else:
        # timestamp is already formatted
        return timestamp

@register.filter
def get_attributes(log):
    """returns the attributes of a log"""
    return dumps(list(log.get_properties().keys()))

@register.filter
def get_operations(attribute_list):
    """returns list of supported operations on the attribute list"""
    for attribute in attribute_list:
        if not isinstance(attribute, Number):
            # for strings only equal and not equal are supported
            return ['=', '≠']
    # for numbers we also add greater / smaller than
    return ['<', '>', '=', '≠']