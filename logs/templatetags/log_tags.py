from django import template
from ..models import LogMetrics, ComparisonMetrics, LogObjectHandler, Log
import json
from helpers.g6_helpers import dfg_dict_to_g6, highlight_nonstandard_activities
from helpers.dfg_helper import convert_dfg_to_dict

register = template.Library()

@register.simple_tag
def unique_id_for_filter(pk, forloopcounter):
    return str(pk)+"-"+str(forloopcounter)


@register.filter
def index(indexable, index):
    return indexable[index]

@register.filter
def create_ref_url(url, ref):
    return "&".join(url.strip().split("&")[0:-1]) + "&ref=" + str(ref)

@register.filter
def get_metrics(log, reference):
    if log == reference:
        return LogMetrics(log.pm4py_log()).get_metrics()
    else:
        return ComparisonMetrics(log.pm4py_log(), reference.pm4py_log()).get_comparison()


@register.filter
def get_graph(log, reference):
    return json.dumps(
        highlight_nonstandard_activities(
            dfg_dict_to_g6(
                convert_dfg_to_dict(
                    LogObjectHandler(log).generate_dfg())), 
                    dfg_dict_to_g6(
                        convert_dfg_to_dict(
                            LogObjectHandler(reference).generate_dfg()))))
