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
from pm4py import discover_directly_follows_graph
from pm4py import get_event_attribute_values
from helpers.dfg_helper import convert_dfg_to_dict
from helpers.g6_helpers import dfg_dict_to_g6
from django.forms.models import model_to_dict

# Create your models here.
class Log(models.Model):
    """
    Model of a log file

    Attributes:
    log_file (linked file)
    log_name (name of the log)

    Functions:
    filename() -> returns name of the log
    pm4py_log() -> returns the converted log using the pm4py and pandas libraries
    """
    log_file = models.FileField(upload_to='logs')
    log_name = models.CharField(max_length=500)
    def filename(self):
        """returns name of log"""
        return basename(self.log_file.name)
    def pm4py_log(self):
        """returns converted log"""
        _, extension = splitext(self.log_file.path)
        if extension == ".csv":
            log = pd.read_csv(self.log_file.path, sep=",")
            log = dataframe_utils.convert_timestamp_columns_in_df(log)
            log = log_converter.apply(log)
        else:
            log = xes_importer_factory.apply(self.log_file.path)
        return log


class LogObjectHandler():
    """
    Model of a log object handler
    used for working with logs from the backend

    Attributes:
    log_object (a log model)
    log (the converted log)

    Functions:
    __init__(log_object) -> sets the attributes according to the log_object
    pm4py_log() -> returns the log attribute
    pk() -> returns the primary key of the log
    to_df() -> returns the date frame conversion of the log
    get_properties() -> returns the properties of the log file
    generate_dfg() -> returns the dfg of the log
    g6() -> returns the g6 visualization of the log
    to_dict() -> returns the log parsed into a dictionary and adds the g6 visualization and properties
    """
    log_object = None
    log = None
    
    def __init__(self, log_object):
        """creates new LogObjectHandler instance"""
        self.log_object = log_object
        self.log = log_object.pm4py_log()
    
    def pm4py_log(self):
        """returns parsed log"""
        return self.log
    
    def pk(self):
        """returns logs primary key"""
        return self.log_object.pk

    def to_df(self):
        """converts log to df"""
        return log_to_data_frame.apply(self.log)

    def get_properties(self):
        """returns properties of log"""
        log_df = self.to_df()
        results = {}

        for columName, columValue in log_df.iteritems():
            values_w_o_na = columValue.dropna()
            results[columName] = list(set(values_w_o_na))
        return results
    
    def generate_dfg(self, percentage_most_freq_edges=100, type=dfg_discovery.Variants.FREQUENCY):
        """generates the dfg of the log"""
        log = self.pm4py_log()
        dfg, sa, ea = discover_directly_follows_graph(log)
        activities_count = get_event_attribute_values(log, "concept:name")
        dfg, sa, ea, activities_count = dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, activities_count, percentage_most_freq_edges)
        return dfg
    
    def g6(self):
        """converts to g6"""
        return dfg_dict_to_g6(convert_dfg_to_dict(self.generate_dfg()))

    def to_dict(self):
        """converts to dictionary"""
        ret = model_to_dict(self.log_object)
        ret['g6'] = self.g6()
        ret['properties'] = self.get_properties()
        return ret