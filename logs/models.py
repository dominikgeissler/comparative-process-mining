from django.db import models
from os.path import basename, splitext
import pandas as pd
from pm4py.algo.filtering.log import attributes
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer_factory
from pm4py.objects.conversion.log.variants import (
    to_data_frame
    as log_to_data_frame)
from pm4py.algo.filtering.dfg import dfg_filtering
from pm4py.statistics.traces.generic.log import case_statistics
import pm4py
from pm4py import discover_directly_follows_graph
from pm4py import get_event_attribute_values
from helpers.dfg_helper import convert_dfg_to_dict
from helpers.g6_helpers import dfg_dict_to_g6, highlight_nonstandard_activities
from helpers.metrics_helper import get_difference, get_difference_days_hrs_min, days_hours_minutes
from filecmp import cmp
import json

# Attributes for metrics
order = ["no_cases",
         "no_events",
         "no_variants",
         "no_activities",
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
        # two logs are equal, if their associated log files are equal
        return cmp(self.log_file.path, other.log_file.path)

    def __hash__(self):
        # due to overwriting the __eq__ function, the __hash__ function
        # needs to be set as well
        # (Django overwrites it)
        return super().__hash__()

class Filter(models.Model):
    """Filter for a log"""
    # percentage field
    percentage = models.IntegerField(default=100)
    
    # string description of the filter type
    type = models.CharField(max_length=500, null=True, default=None)
    # for attribute-filter
    attribute = models.CharField(max_length=500, null=True,default=None)

    # for case-performance filter
    case_performance1 = models.IntegerField(null=True,default=None)
    case_performance2 = models.IntegerField(null=True,default=None)

    # for between filter
    case1 = models.CharField(max_length=500, null=True,default=None)
    case2 = models.CharField(max_length=500, null=True,default=None)

    # for case-size filter
    case_size1 = models.IntegerField(null=True,default=None)
    case_size2 = models.IntegerField(null=True,default=None)

    # for timestamp
    timestamp1 = models.CharField(max_length=500, null=True)
    timestamp2 = models.CharField(max_length =500, null=True)

    # parsed timestamps
    timestamp1_parsed = models.DateTimeField(null=True)
    timestamp2_parsed = models.DateTimeField(null=True)

    def set_attribute(self, attr, value):
        """set attribute(s) to value"""
        # if a list of keys is given, set each key to the corresponding
        # value key with index(key) = index(value)
        if isinstance(attr,list):
            for i, at in enumerate(attr):
                setattr(self, at, value[i])
                if "timestamp" in at:
                    from dateutil.parser import parse
                    setattr(self, at+"_parsed", parse(value[i]).strftime("%Y-%m-%d %H:%M"))
        else:
            # since no list was given, just set the single attribute
            setattr(self, attr, value)


class LogObjectHandler(models.Model):
    """Handler for log object in comparison page"""
    log_object = models.ForeignKey(Log,
                                   on_delete=models.CASCADE)
    filter = models.OneToOneField(Filter, null=True, on_delete=models.SET_NULL)

    def to_df(self):
        """converts log to df"""
        return log_to_data_frame.apply(self.pm4py_log())

    def get_activities(self):
        return pm4py.get_attribute_values(self.pm4py_log(), "concept:name")

    def get_properties(self):
        """returns properties of log"""
        log_df = self.to_df()
        results = {}

        for columName, columValue in log_df.iteritems():
            values_w_o_na = columValue.dropna()
            results[columName] = list(set(values_w_o_na))
        return results

    def get_timestamps(self):
        return sorted(pm4py.get_attribute_values(self.pm4py_log(), "time:timestamp"))
        
    def get_similarity_index(self, reference):
        if reference and reference.log_object != self.log_object:
            act_count1 = pm4py.get_attribute_values(
                self.pm4py_log(), "concept:name")
            act_count2 = pm4py.get_attribute_values(
                reference.pm4py_log(), "concept:name")
            different_activities = 0
            for key in act_count1:
                if key in act_count2.keys():
                    different_activities += abs(
                        act_count1[key] - act_count2[key])
                else:
                    different_activities += act_count1[key]
            if different_activities > sum(act_count1.values()):
                different_activities = sum(act_count1.values())
            res_similar_activities1 = (
                sum(act_count1.values()) - different_activities)/sum(act_count1.values())
            """
            Calculation of the number of similar activities in comparison to the 
            sum of all activities in act_count1 (Dictionary activities_count).
            Special feature: 
            The index emphasis the size of the log.
            The index is higher if the analyzed log has fewer events compared to the reference log.
            And the index is lower if the analyzed log has more events than the reference log.
            """
            similar_activities = 0
            for key in act_count1:
                if key in act_count2.keys():
                    similar_activities += 1
            res_similar_activities2 = similar_activities/len(act_count1)
            """
            Calculation of the number of similar activities in comparison to the 
            number of activities in act_count1 (Dictionary activities_count).
            Special feature: 
            This index focuses on the number of similar activities (not how often they occur)
            and neglects the size of or size difference between the two event logs.
            """
            res = (res_similar_activities1 + res_similar_activities2)/2
            return str("%.2f" % round(res*100, 2))+"%"
            """
            Result = Similarity index:
            50% weighting with emphasis on the size or size difference between the logs.
            And 50% weighting without focusing on the size or size difference of the two logs.
            """
        return "100%"

    def pm4py_log(self):
        """return parsed log"""
        return self.log_object.pm4py_log()

    def log_name(self):
        """return name of the log"""
        return self.log_object.log_name

    def generate_dfg(self):
        """generates the dfg of the log"""
        log = self.pm4py_log()
        # default value for pm4py dfg discovery
        percentage_most_freq_edges = 100

        # if a filter was selected
        if self.filter:
            # if something wents wrong while filtering,
            # the filter is ignored
            filtered_log = None
            # 'switch' over implemeneted filters
            if self.filter.type == "variant_percentage":
                from pm4py.algo.filtering.log.variants import variants_filter
                filtered_log = variants_filter.filter_log_variants_percentage(log, percentage=self.filter.percentage/100)
            elif self.filter.type == "variant_coverage_percentage":
                from pm4py.algo.filtering.log.variants import variants_filter
                filtered_log = variants_filter.filter_variants_by_coverage_percentage(log, self.filter.percentage/100)
            elif self.filter.type == "attribute_filter":
                from pm4py.algo.filtering.log.attributes import attributes_filter
                filtered_log = attributes_filter.apply_auto_filter(log, parameters={
                attributes_filter.Parameters.ATTRIBUTE_KEY: self.filter.attribute, attributes_filter.Parameters.DECREASING_FACTOR: self.filter.percentage/100})
            elif self.filter.type == "case_performance":
                from pm4py.algo.filtering.log.cases import case_filter
                filtered_log = case_filter.filter_case_performance(log, self.filter.case_performance1, self.filter.case_performance2)
            elif self.filter.type == "between_filter"  :
                import pm4py
                filtered_log = pm4py.filter_between(log, self.filter.case1, self.filter.case2)    
            elif self.filter.type == "case_size":
                import pm4py
                filtered_log = pm4py.filter_case_size(log, self.filter.case_size1, self.filter.case_size2)
            elif self.filter.type == "timestamp_filter_contained":
                from pm4py.algo.filtering.log.timestamp import timestamp_filter
                filtered_log = timestamp_filter.filter_traces_contained(log, self.filter.timestamp1_parsed, self.filter.timestamp2_parsed)
            elif self.filter.type == "timestamp_filter_intersecting":
                from pm4py.algo.filtering.log.timestamp import timestamp_filter
                filtered_log = timestamp_filter.filter_traces_intersecting(log, self.filter.timestamp1_parsed, self.filter.timestamp2_parsed)

            # since the filtered log is only set if a filter was applied,
            # and thus not None, otherwise the filter is ignored
            if filtered_log:
                log = filtered_log

        dfg, sa, ea = discover_directly_follows_graph(log)
        activities_count = get_event_attribute_values(log, "concept:name")

        dfg, sa, ea,
        activities_count = dfg_filtering.filter_dfg_on_paths_percentage(
            dfg, sa, ea, activities_count, percentage_most_freq_edges)
        return dfg

    def metrics(self, reference=None):
        """returns the metrics of a log
        or the comparison relative to the reference"""
        # get the global list of attributes
        global order
        # calculate the metrics for linked log
        metrics1 = LogMetrics(self.pm4py_log())
        # if a reference was selected and the reference is different
        # to linked log, calulate the metrics for the reference
        # log as well and return the metrics of the linked log
        # and the difference relative to the reference log
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
        # since no reference log was given (or the refrence log is
        # equal to the linked log) return the metrics of the linked log
        return vars(Metrics([
            getattr(metrics1, attr)
            if 'duration' not in attr
            else
            days_hours_minutes(getattr(metrics1, attr))
            for attr in order]))

    def graph(self, reference=None):
        """returns the graph of a log object
        or return the graph of a log object with
        highlighted nodes relative to reference"""
        # if a reference log is selected (and its different than the
        # linked log), highlight the non-standard activites
        # (e.g. the activites in the reference log that are not
        # present in the linked log) and then calculate the g6-graph.
        # Otherwise just calculate the g6-graph
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
        # if no filter exists
        if not self.filter:
            # create filter
            self.filter = Filter.objects.create()
            # save created filter
            self.filter.save()
        # set the attribute(s) of the filter and save it 
        self.filter.set_attribute(attr, value)
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

        activities_count = pm4py.get_attribute_values(log, "concept:name")
        """PM4Py library function"""
        self.no_activities = len(activities_count)
        """Number of Activities"""

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
