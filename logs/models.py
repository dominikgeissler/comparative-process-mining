from django.db import models
from os.path import basename, splitext
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer_factory
from pm4py.objects.conversion.log.variants import (
    to_data_frame
    as log_to_data_frame)
from pm4py.statistics.traces.generic.log import case_statistics
import pm4py
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
         "average_case_duration",
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
    # string description of the filter type
    type = models.CharField(max_length=500, null=True, default=None)
    
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
    timestamp1 = models.DateTimeField(null=True)
    timestamp2 = models.DateTimeField(null=True)

    # frequency / performance
    isFrequency = models.BooleanField(default=True)

    # attribute filter
    attribute = models.CharField(max_length=500, null=True)
    attribute_value = models.CharField(max_length=500, null=True)
    operator = models.CharField(max_length=500, null=True)

    def set_attribute(self, attr, value):
        """set attribute(s) to value"""
        # if a list of keys is given, set each key to the corresponding
        # value key with index(key) = index(value)
        if isinstance(attr,list):
            for i, at in enumerate(attr):
                setattr(self, at, value[i])
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
        """
        Similarity Index based on the number of common variants or (in other words) common traces
        """
        if reference and reference.generate_dfg(only_extract_filtered_log=True) != self.generate_dfg(only_extract_filtered_log=True):
            variants_count_log = case_statistics.get_variant_statistics(
                self.generate_dfg(only_extract_filtered_log=True))
            variants_count_reference = case_statistics.get_variant_statistics(
                reference.generate_dfg(only_extract_filtered_log=True))
            sum_variants_reference = 0
            sum_variants_log = 0
            common_no_variants = 0
            for x in range(0, len(variants_count_reference)-1):
                for i in range(0, len(variants_count_log)-1):
                    # if variants_count_reference[x]['variant'] == variants_count_log[i]['variant']:
                    if variants_count_reference[x]['variant'] in variants_count_log[i]['variant']:
                        common_no_variants += min(
                            variants_count_reference[x]['count'], variants_count_log[i]['count'])
                sum_variants_reference += variants_count_reference[x]['count']
            for i in range(0, len(variants_count_log)-1):
                sum_variants_log += variants_count_log[i]['count']
            sum = max(sum_variants_reference, sum_variants_log)
            return str("%.2f" % round(common_no_variants/sum*100, 2))+"%"
        return "100%"

    def pm4py_log(self):
        """return parsed log"""
        return self.log_object.pm4py_log()

    def log_name(self):
        """return name of the log"""
        return self.log_object.log_name

    def generate_dfg(self, only_extract_filtered_log=False):
        """generates the dfg of the log"""
        log = self.pm4py_log()
        # if a filter was selected
        if self.filter:
            # if something wents wrong while filtering,
            # the filter is ignored
            filtered_log = None
            # 'switch' over implemeneted filters
            if self.filter.type == "case_performance":
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
                from django.utils.timezone import make_naive
                from pytz import UTC
                # normalize timestamps
                timestamp1, timestamp2 = make_naive(self.filter.timestamp1, UTC), make_naive(self.filter.timestamp2, UTC)
                filtered_log = timestamp_filter.filter_traces_contained(log, timestamp1,timestamp2) 
            elif self.filter.type == "timestamp_filter_intersecting":
                from django.utils.timezone import make_naive
                from pm4py.algo.filtering.log.timestamp import timestamp_filter
                from pytz import UTC
                # normalize timestamps
                timestamp1, timestamp2 = make_naive(self.filter.timestamp1, UTC), make_naive(self.filter.timestamp2, UTC)
                filtered_log = timestamp_filter.filter_traces_intersecting(log, timestamp1,timestamp2)
            elif self.filter.type == "filter_on_attributes":
                from pm4py.algo.filtering.log.attributes import attributes_filter
                import math
                if self.filter.operator == "=":
                    try:
                        parsed_val = float(self.filter.attribute_value)
                        filtered_log = attributes_filter.apply(log, [parsed_val],
                                          parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: self.filter.attribute, attributes_filter.Parameters.POSITIVE: True})
                    except:
                        filtered_log = attributes_filter.apply(log, [self.filter.attribute_value],
                                          parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: self.filter.attribute, attributes_filter.Parameters.POSITIVE: True})
                elif self.filter.operator == "≠":
                    try:
                        parsed_val = float(self.filter.attribute_value)
                        filtered_log = attributes_filter.apply(log, [parsed_val],
                                          parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: self.filter.attribute, attributes_filter.Parameters.POSITIVE: False})
                    except:
                        filtered_log = attributes_filter.apply(log, [self.filter.attribute_value],
                                          parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: self.filter.attribute, attributes_filter.Parameters.POSITIVE: False})
                elif self.filter.operator == "<":
                    filtered_log = attributes_filter.apply_numeric_events(log, -math.inf, float(self.filter.attribute_value),
                                             parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: self.filter.attribute})
                elif self.filter.operator == ">":
                    filtered_log = attributes_filter.apply_numeric_events(log, float(self.filter.attribute_value), math.inf,
                                             parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: self.filter.attribute})

            
            # since the filtered log is only set if a filter was applied,
            # and thus not None, otherwise the filter is ignored
            if filtered_log:
                log = filtered_log
        if only_extract_filtered_log:
            return log

        from pm4py.algo.discovery.dfg import algorithm as dfg_discovery

        variant = dfg_discovery.Variants.FREQUENCY\
                if not self.filter or self.filter.isFrequency\
                else dfg_discovery.Variants.PERFORMANCE
        
        dfg = dfg_discovery.apply(log, variant=variant)
        return dfg

    def metrics(self, reference=None):
        """returns the metrics of a log
        or the comparison relative to the reference"""
        # get the global list of attributes
        global order
        # calculate the metrics for linked log
        # if a filter is applied, calculate the metrics for the filtered log
        metrics1 = LogMetrics(self.generate_dfg(only_extract_filtered_log=True))
        # if a reference was selected and the reference is different
        # to linked log, calulate the metrics for the reference
        # log as well and return the metrics of the linked log
        # and the difference relative to the reference log

        if reference and self.generate_dfg(only_extract_filtered_log=True) != reference.generate_dfg(only_extract_filtered_log=True):
            # if reference is filtered, calculate comparison for filtered 
            metrics2 = LogMetrics(reference.generate_dfg(only_extract_filtered_log=True))
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
        # since no reference log was given (or the reference log is
        # equal to the linked log) return the metrics of the linked log
        return vars(Metrics([
            getattr(metrics1, attr)
            if 'duration' not in attr
            else
            days_hours_minutes(getattr(metrics1, attr))
            for attr in order]))

    def graph(self, reference=None):
        """returns the graph of a log object
        or returns the graph of a log object with
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
        # set the attribute(s) of the filter and save it 
        self.filter.set_attribute(attr, value)
        self.filter.save()

    def get_isFrequency(self):
        # unnötig -> kannst du im template machen mit
        # {% if not filter or filter.isFrequency  %}
        # blabla frequency
        # {% else %}
        # blabla performance
        # ...
        if self.filter is None or self.filter.isFrequency == True:
            return "Frequency"
        else:
            return "Performance"

    def get_filter(self):
        # alles ins template verlagern
        if self.filter is None:
            return {"No filter selected": "No attribute(s) selected"}
        elif self.filter.type == "case_performance":
            return {"Case Performance": "Between " + str(self.filter.case_performance1) + " and " + str(self.filter.case_performance2)}
        elif self.filter.type == "between_filter":
            return {"Between Filter": "Between '" + str(self.filter.case1) + "' and '" + str(self.filter.case2)+"'"}
        elif self.filter.type == "case_size":
            return {"Case Size": "Between " + str(self.filter.case_size1) + " and " + str(self.filter.case_size2)}
        elif self.filter.type == "timestamp_filter_contained":
            from django.utils.timezone import make_naive
            from pytz import UTC
            timestamp1, timestamp2 = make_naive(
                self.filter.timestamp1, UTC), make_naive(self.filter.timestamp2, UTC)
            return {"Timestamp Filter (contained)": "Between " + str(timestamp1) + " and " + str(timestamp2)}
        elif self.filter.type == "timestamp_filter_intersecting":
            from django.utils.timezone import make_naive
            from pytz import UTC
            # brauchst du nicht
            timestamp1, timestamp2 = make_naive(
                self.filter.timestamp1, UTC), make_naive(self.filter.timestamp2, UTC)
            return {"Timestamp Filter (intersecting)": "Between " + str(timestamp1) + " and " + str(timestamp2)}
        elif self.filter.type == "filter_on_attributes":
            # warum diese fallunterscheidung und nicht einfach
            # return str(self.filter.attribute) + self.filter.operator + ...
            if self.filter.operator == "=":
                return {"Filter on attributes": str(self.filter.attribute) + " = " + str(self.filter.attribute_value)}
            elif self.filter.operator == "≠":
                return {"Filter on attributes": str(self.filter.attribute) + " ≠ " + str(self.filter.attribute_value)}
            elif self.filter.operator == "<":
                return {"Filter on attributes": str(self.filter.attribute) + " < " + str(self.filter.attribute_value)}
            elif self.filter.operator == ">":
                return {"Filter on attributes": str(self.filter.attribute) + " > " + str(self.filter.attribute_value)}


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
        self.average_case_duration = avg_case_duration
        """Average Case Duration"""

        median_case_duration = (
            case_statistics.get_median_caseduration(
                self.log, parameters={
                    case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"}))
        """PM4Py library function"""
        self.median_case_duration = median_case_duration
        """Median Case Duration"""
