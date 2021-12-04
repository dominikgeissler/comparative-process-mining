from django.db import models
from os.path import basename, splitext
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer_factory
from pm4py.objects.conversion.log.variants import (
    to_data_frame
    as log_to_data_frame)
from pm4py.algo.filtering.dfg import dfg_filtering
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py import discover_directly_follows_graph
from pm4py import get_event_attribute_values
from helpers.dfg_helper import convert_dfg_to_dict
from helpers.g6_helpers import dfg_dict_to_g6, highlight_nonstandard_activities
from helpers.metrics_helper import get_difference, get_difference_days_hrs_min
from filecmp import cmp
import json

# Attributes for metrics
order = ["no_cases", 
        "no_events", 
        "no_variants", 
        "avg_case_duration", 
        "median_case_duration", 
        "total_case_duration"]


class Log(models.Model):
    """A log with linked file"""
    log_file = models.FileField(upload_to='logs')
    log_name = models.CharField(max_length=500)

    def filename(self):
        return basename(self.log_file.name)

    def pm4py_log(self):
        """parse log"""
        _, extension = splitext(self.log_file.path)
        if extension == ".csv":
            log = pd.read_csv(self.log_file.path, sep=",")
            log = dataframe_utils.convert_timestamp_columns_in_df(log)
            log = log_converter.apply(log)
        else:
            log = xes_importer_factory.apply(self.log_file.path)
        return log
    
    def __eq__(self, other):
        return cmp(self.log_file.path, other.log_file.path)

    def __hash__(self):
        return super().__hash__()

class Filter(models.Model):
    """Filter for a log"""
    percentage = models.FloatField(default=100)

    def set_attribute(self, attr, value):
        """set attribute to value"""
        setattr(self,attr,value)

class LogObjectHandler(models.Model):
    """Handler for log object in comparison page"""
    log_object = models.ForeignKey(Log,
      on_delete=models.CASCADE)
    filter = models.OneToOneField(Filter, null=True, on_delete=models.SET_NULL)

    def to_df(self):
        """converts log to df"""
        return log_to_data_frame.apply(self.pm4py_log())

    def get_properties(self):
        """returns properties of log"""
        log_df = self.to_df()
        results = {}

        for columName, columValue in log_df.iteritems():
            values_w_o_na = columValue.dropna()
            results[columName] = list(set(values_w_o_na))
        return results

    def pm4py_log(self):
        """return parsed log"""
        return self.log_object.pm4py_log()

    def log_name(self):
        """return name of the log"""
        return self.log_object.log_name  

    def generate_dfg(self, percentage_most_freq_edges=100):
        """generates the dfg of the log"""
        log = self.pm4py_log()
        dfg, sa, ea = discover_directly_follows_graph(log)
        activities_count = get_event_attribute_values(log, "concept:name")

        dfg, sa, ea,
        activities_count = dfg_filtering.filter_dfg_on_paths_percentage(
            dfg, sa, ea, activities_count, percentage_most_freq_edges)
        return dfg

    def metrics(self, reference=None):
        """returns the metrics of a log
        or the comparison relative to the reference"""
        global order
        metrics1 = LogMetrics(self.pm4py_log())
        if reference and reference.log_object != self.log_object:
            metrics2 = LogMetrics(reference.pm4py_log())
            return vars(Metrics([
            get_difference(
                getattr(metrics1, attr),
                getattr(metrics2, attr)
             )
            if 'duration' not in attr 
            else
            get_difference_days_hrs_min(
                getattr(metrics1, attr),
                getattr(metrics2, attr))
            for attr in order
            ]))
        return vars(Metrics([
            getattr(metrics1, attr)
         for attr in order]))


    def graph(self, reference=None):
        """returns the graph of a log object
        or return the graph of a log object with 
        highlighted nodes relative to reference"""
        if reference and reference.log_object != self.log_object:
            return json.dumps(
                highlight_nonstandard_activities(
                    dfg_dict_to_g6(
                        convert_dfg_to_dict(
                            self.generate_dfg()
                        )
                    ), 
                    dfg_dict_to_g6(
                        convert_dfg_to_dict(
                            reference.generate_dfg()
                        )
                    )
                )
            )
        return json.dumps(
            dfg_dict_to_g6(
                convert_dfg_to_dict(
                    self.generate_dfg()
                )
            )
        )
    def set_filter(self, attr, value):
        """set filter of log (or create and then 
        set if, if it doesnt exist)"""
        if not self.filter:
            self.filter = Filter.objects.create()
            self.filter.save()
        self.filter.set_attribute(attr,value)
        self.filter.save()


class Metrics():
    """
    Class for ordered return (and refactoring)
    """
    def __init__(self, metrics):
        global order
        for index, metric in enumerate(metrics):
            setattr(self, order[index], metric)

class LogMetrics():
    """
    Calculates the metrics for a given log
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
        self.total_case_duration = (sum(all_case_durations))
        """Total Case Duration"""

        if self.no_cases <= 0:
            avg_case_duration = 0
        else:
            avg_case_duration = (sum(all_case_durations)) / self.no_cases
        self.avg_case_duration = avg_case_duration
        """Average Case Duration"""

        median_case_duration = (
            case_statistics.get_median_caseduration(
                self.log, parameters={
                    case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"}))
        """PM4Py library function"""
        self.median_case_duration = median_case_duration
        """Median Case Duration"""
