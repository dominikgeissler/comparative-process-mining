from django import template
from pytz import timezone

register = template.Library()
formatstring = "%Y-%m-%d %H:%M:%S"
utc = timezone('UTC')

@register.filter
def convert_timestamp(timestamp):
    return timestamp.strftime(formatstring)