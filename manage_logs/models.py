from django.db import models
from django.conf import settings
from os.path import basename, splitext
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer_factory
from pm4py.objects.conversion.log.variants import to_data_frame as log_to_data_frame
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.filtering.dfg import dfg_filtering
from pm4py import discover_directly_follows_graph, get_event_attribute_value
from helpers.dfg_helper import convert_dfg_to_dict
from helpers.g6_helpers import dfg_dict_to_g6
from django.forms.models import model_to_dict

# Create your models here.
class Log(models.Model):
    log_file = models.FileField(upload_to=settings.EVENT_LOG_URL)
    log_name = models.CharField()
    def filename(self):
        return basename(self.log_file.name)
    def pm4py_log(self):
        _, extension = splitext(self.log_file.path)
        if extension == ".csv":
            log = pd.read_csv(self.log_file.path, sep=",")
            log = dataframe_utils.convert_timestamp_columns_in_df(log)
            log = log_converter.apply(log)
        else:
            log = xes_importer_factory.apply(self.log_file.path)


class LogObjectHandler():
    log_object = None
    log = None
    
    def __init__(self, log_object):
        self.log_object = log_object
        self.log = log_object.pm4py_log()
    
    def pm4py_log(self):
        return self.log
    
    def pk(self):
        return self.log_object.pk

    def to_df(self):
        return log_to_data_frame.apply(self.log)

    def get_properties(self):
        log_df = self.to_df()
        results = {}

        for columName, columValue in log_df.iteritems():
            values_w_o_na = columValue.dropna()
            results[columName] = list(set(values_w_o_na))
        return results
    
    def generate_dfg(self, percentage_most_freq_edges=100, type=dfg_discovery.Variants.FREQUENCY):
        log = self.pm4py_log()
        dfg, sa, ea = discover_directly_follows_graph(log)
        activities_count = get_event_attribute_value(log, "concept:name")
        dfg, sa, ea, activities_count = dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, activities_count, percentage_most_freq_edges)
        return dfg
    
    def g6(self):
        return dfg_dict_to_g6(convert_dfg_to_dict(self.generate_dfg()))

    def convert_dfg_to_dict(self):
        ret = model_to_dict(self.log_object)
        ret['g6'] = self.g6()
        ret['properties'] = self.get_properties()
        return ret