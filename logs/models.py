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
from helpers.metrics_helper import days_hours_minutes, get_total_pct
from django.forms.models import model_to_dict


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
    """Metrics for a single log"""

    def __init__(self, log):
        self.log = log
        self.no_cases = len(self.log)

        self.no_events = sum([len(trace) for trace in self.log])

        variants_count = case_statistics.get_variant_statistics(log)
        self.no_variants = len(variants_count)

        all_case_durations = case_statistics.get_all_casedurations(
            self.log, parameters={
                case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"})
        self.total_case_duration = (sum(all_case_durations))

        if self.no_cases <= 0:
            avg_case_duration = 0
        else:
            avg_case_duration = self.total_case_duration / self.no_cases

        median_case_duration = (
            case_statistics.get_median_caseduration(
                self.log, parameters={
                    case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"}))

        self.avg_case_duration = avg_case_duration
        self.median_case_duration = median_case_duration


def get_metrics(self):
    return {
        'no_cases': self.no_cases,
        'no_events': self.no_events,
        'no_variants': self.no_variants,
        'avg_case_duration': self.avg_case_duration,
        'median_case_duration': self.median_case_duration,
        'total_case_duration': self.total_case_duration
    }


class ComparisonMetrics(models.Model):

    def __init__(self, log1, log2):
        self.metrics1 = LogMetrics(log1)
        self.metrics2 = LogMetrics(log2)
        self.no_cases1_total, self.no_cases1_pct = get_total_pct(
            self.metrics1.no_cases, self.metrics2.no_cases)
        self.no_cases2_total, self.no_cases2_pct = get_total_pct(
            self.metrics2.no_cases, self.metrics1.no_cases)

        # Total and Percentage Difference concerning Number of Events:
        self.no_events1_total, self.no_events1_pct = get_total_pct(
            self.metrics1.no_events, self.metrics2.no_events)
        self.no_events2_total, self.no_events2_pct = get_total_pct(
            self.metrics2.no_events, self.metrics1.no_events)

        # Total and Percentage Difference regarding Number of Variants:
        self.no_variants1_total, self.no_variants1_pct = get_total_pct(
            self.metrics1.no_variants, self.metrics2.no_variants)
        self.no_variants2_total, self.no_variants2_pct = get_total_pct(
            self.metrics2.no_variants, self.metrics1.no_variants)

        # Total and Percentage Difference of Total Case Duration:
        tcd1_t, tcd1_p = get_total_pct(
            self.metrics1.total_case_duration, self.metrics2.total_case_duration)
        tcd2_t, tcd2_p = get_total_pct(
            self.metrics2.total_case_duration, self.metrics1.total_case_duration)
        self.total_case_duration1_total = days_hours_minutes(tcd1_t)
        self.total_case_duration1_pct = get_pct(tcd1_p)
        self.total_case_duration2_total = days_hours_minutes(tcd2_t)
        self.total_case_duration2_pct = get_pct(tcd2_p)

        # Total and Percentage Difference of Average Case Duration:
        acd1_t, acd1_p = get_total_pct(
            self.metrics1.avg_case_duration, self.metrics2.avg_case_duration)
        acd2_t, acd2_p = get_total_pct(
            self.metrics2.avg_case_duration, self.metrics1.avg_case_duration)
        self.avg_case_duration1_total = days_hours_minutes(acd1_t)
        self.avg_case_duration1_pct = get_pct(acd1_p)
        self.avg_case_duration2_total = days_hours_minutes(acd2_t)
        self.avg_case_duration2_pct = get_pct(acd2_p)

        # Total and Percentage Difference of Median Case Duration:
        mcd1_t, mcd1_p = get_total_pct(
            self.metrics1.median_case_duration, self.metrics2.median_case_duration)
        mcd2_t, mcd2_p = get_total_pct(
            self.metrics2.median_case_duration, self.metrics1.median_case_duration)
        self.median_case_duration1_total = days_hours_minutes(mcd1_t)
        self.median_case_duration1_pct = get_pct(mcd1_p)
        self.median_case_duration2_total = days_hours_minutes(mcd2_t)
        self.median_case_duration2_pct = get_pct(mcd2_p)

    def get_comparison(self):
        return {
            'no_cases1_total': self.no_cases1_total,
            'no_cases2_total': self.no_cases2_total,
            'no_cases1_pct': self.no_cases1_pct,
            'no_cases2_pct': self.no_cases2_pct,
            'no_events1_total': self.no_events1_total,
            'no_events2_total': self.no_events2_total,
            'no_events1_pct': self.no_events1_pct,
            'no_events2_pct': self.no_events2_pct,
            'no_variants1_total': self.no_variants1_total,
            'no_variants2_total': self.no_variants2_total,
            'no_variants1_pct': self.no_variants1_pct,
            'no_variants2_pct': self.no_variants2_pct,
            'total_case_duration1_total': self.total_case_duration1_total,
            'total_case_duration2_total': self.total_case_duration2_total,
            'total_case_duration1_pct': self.total_case_duration1_pct,
            'total_case_duration2_pct': self.total_case_duration2_pct,
            'avg_case_duration1_total': self.avg_case_duration1_total,
            'avg_case_duration2_total': self.avg_case_duration2_total,
            'avg_case_duration1_pct': self.avg_case_duration1_pct,
            'avg_case_duration2_pct': self.avg_case_duration2_pct,
            'median_case_duration1_total': self.median_case_duration1_total,
            'median_case_duration2_total': self.median_case_duration2_total,
            'median_case_duration1_pct': self.median_case_duration1_pct,
            'median_case_duration2_pct': self.median_case_duration2_pct
        }
