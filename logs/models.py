from django.db import models
from os.path import basename, splitext
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer_factory
from pm4py.objects.conversion.log.variants import (
    to_data_frame
    as log_to_data_frame)
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.filtering.dfg import dfg_filtering
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py import discover_directly_follows_graph
from pm4py import get_event_attribute_values
from helpers.dfg_helper import convert_dfg_to_dict
from helpers.g6_helpers import dfg_dict_to_g6
from helpers.metrics_helper import days_hours_minutes, get_difference, get_difference_days_hrs_min
from django.forms.models import model_to_dict
from filecmp import cmp


class Log(models.Model):
    """
    Model of a log file

    Attributes:
    log_file (linked file)
    log_name (name of the log)

    Functions:
    filename() -> returns name of the log
    pm4py_log() -> returns the converted log using the pm4py
    and pandas libraries
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
    
    def __eq__(self, other):
        return cmp(self.log_file, other.log_file)


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

    to_dict() -> returns the log parsed into a dictionary
    and adds the g6 visualization and properties
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

    def generate_dfg(self,
                     percentage_most_freq_edges=100,
                     type=dfg_discovery.Variants.FREQUENCY):
        """generates the dfg of the log"""
        log = self.pm4py_log()
        dfg, sa, ea = discover_directly_follows_graph(log)
        activities_count = get_event_attribute_values(log, "concept:name")

        dfg, sa, ea,
        activities_count = dfg_filtering.filter_dfg_on_paths_percentage(
            dfg, sa, ea, activities_count, percentage_most_freq_edges)
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


class LogMetrics(models.Model):
    """
    Metrics for a single log
    get_metrics(self) -> return of values
    """

    def __init__(self, log):
        self.log = log
        self.no_cases = len(self.log)
        """Number of Cases"""

        self.no_events = sum([len(trace) for trace in self.log])
        """Number of Events"""
        """
        Explanation of the calculation:
        First, with "for trace in self.log" get the different traces in the event log.
        Second, with "len(trace)" calculated the number of events
        (via the length of the trace) in every trace.
        Third, with "sum(...)" sum up all the number of events of all traces.
        """

        variants_count = case_statistics.get_variant_statistics(log)
        """PM4Py library function"""
        self.no_variants = len(variants_count)
        """Number of Variants"""

        all_case_durations = case_statistics.get_all_casedurations(
            self.log, parameters={
                case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"})
        """PM4Py library function"""
        self.total_case_duration = days_hours_minutes(sum(all_case_durations))
        """Total Case Duration"""

        if self.no_cases <= 0:
            avg_case_duration = 0
        else:
            avg_case_duration = (sum(all_case_durations)) / self.no_cases
        self.avg_case_duration = days_hours_minutes(avg_case_duration)
        """Average Case Duration"""

        median_case_duration = (
            case_statistics.get_median_caseduration(
                self.log, parameters={
                    case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"}))
        """PM4Py library function"""
        self.median_case_duration = days_hours_minutes(median_case_duration)
        """Median Case Duration"""

    def get_metrics(self):
        return {
            'no_cases': self.no_cases,
            'no_events': self.no_events,
            'no_variants': self.no_variants,
            'avg_case_duration': self.avg_case_duration,
            'median_case_duration': self.median_case_duration,
            'total_case_duration': self.total_case_duration
        }
# get_metrics(self) -> return values for rendering (only for test purposes)"""


class ComparisonMetrics(models.Model):
    """
    Calculation of metrics regarding the comparison of two logs:
    log1, log2: two handed over event logs (initialized via constructor).
    self.metrics1, self.metrics2: Create new objects to calculate the metrics for each event log.
    Afterwards, calculated all metrics and assign values to variables (still part of constructor).
    All comparison metrics are calculated for the left and right processes. Plus, in total and pct.
    get_comparison(self) -> return of values for rendering
    """

    def __init__(self, log1, log2):
        self.metrics1 = LogMetrics(log1)
        self.metrics2 = LogMetrics(log2)
        """Initailize self.metrics2, self.metrics2 to compare metrcis of both event logs"""

    def get_comparison(self):
        """return of values for rendering"""
        return {
            'no_cases': get_difference(self.metrics1.no_cases, self.metrics2.no_cases),
            'no_events': get_difference(self.metrics1.no_events, self.metrics2.no_events),
            'no_variants': get_difference(self.metrics1.no_variants, self.metrics2.no_variants),
            'avg_case_duration': get_difference_days_hrs_min(self.metrics1.avg_case_duration,
                                                             self.metrics2.avg_case_duration),
            'median_case_duration': get_difference_days_hrs_min(self.metrics1.median_case_duration,
                                                                self.metrics2.median_case_duration),
            'total_case_duration': get_difference_days_hrs_min(self.metrics1.total_case_duration,
                                                               self.metrics2.total_case_duration)
        }

    def check_log_equality(self):
        return self.metrics1.log == self.metrics2.log
