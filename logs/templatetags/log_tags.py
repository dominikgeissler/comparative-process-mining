from django import template
from ..models import LogMetrics, LogObjectHandler, Log
import json
from helpers.g6_helpers import dfg_dict_to_g6, highlight_nonstandard_activities
from helpers.dfg_helper import convert_dfg_to_dict

register = template.Library()


@register.filter
def get_metrics(log):
    log1 = Log.objects.get(pk=1)
    if ComparisonMetrics(log.pm4py_log(), log1.pm4py_log()).check_log_equality():
        return LogMetrics(log.pm4py_log()).get_metrics()
    else:
        return ComparisonMetrics(log.pm4py_log(), log1.pm4py_log()).get_comparison()


@register.filter
def get_graph(log):
    return json.dumps(
        highlight_nonstandard_activities(
            dfg_dict_to_g6(
                convert_dfg_to_dict(
                    LogObjectHandler(log).generate_dfg()))))
