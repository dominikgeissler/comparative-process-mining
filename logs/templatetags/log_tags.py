from django import template
from ..models import LogMetrics, LogObjectHandler, Log
import json
from helpers.g6_helpers import dfg_dict_to_g6, highlight_nonstandard_activities
from helpers.dfg_helper import convert_dfg_to_dict

register = template.Library()

@register.filter
def get_metrics(log):
    return LogMetrics(log.pm4py_log()).get_metrics()


@register.filter
def get_graph(log):
    return json.dumps(
        dfg_dict_to_g6(
            convert_dfg_to_dict(
                LogObjectHandler(log).generate_dfg())))
