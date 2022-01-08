from os.path import splitext
from django.db import models
from django.utils.timezone import make_naive
import pandas as pd
import pm4py
from pm4py.algo.filtering.log.cases import case_filter
from pm4py.algo.filtering.log.timestamp import timestamp_filter
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer_factory
from pm4py.objects.conversion.log.variants import (
    to_data_frame
    as log_to_data_frame)
from pm4py.statistics.traces.generic.log import case_statistics
from filecmp import cmp
import json
from .utils import convert_dfg_to_dict, dfg_dict_to_g6, highlight_nonstandard_activities, get_difference, get_difference_days_hrs_min, days_hours_minutes
from pytz import UTC


# Attributes for metrics
order = ["no_cases",
         "no_events",
         "no_variants",
         "no_activities",
         "average_case_duration",
         "median_case_duration",
         "total_case_duration"]


class Log(models.Model):
    """
    A model to represent an uploaded eventlog

    ---
    Arguments:
        log_file:
            the eventlog file
        log_name:
            the name of the eventlog (default: log_file.name)
    ---
    Properties:
        log_file:
            the eventlog file
        log_name:
            the name of the eventlog
    ---
    Methods:
        pm4py_log(): returns EventLog object of log
    """
    # the file itself
    log_file = models.FileField(upload_to='logs')

    # the name of the file
    log_name = models.CharField(max_length=500)

    def pm4py_log(self):
        """returns an EventLog object of the log file linked to the model"""
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
    """
    A model to represent a filter for a log

    ---
    Properties:
        type (str, opt):
            a representation of the selected filter
        case_performance1 (int, opt):
            lower bound for the case performance filter
        case_performance2 (int, opt):
            upper bound for the case performance filter
        case1 (str, opt):
            start case for the between filter
        case2 (str, opt):
            end case for the between filter
        case_size1 (int, opt):
            lower bound for the case size filter
        case_size2 (int, opt):
            upper bound for the case size filter
        timestamp1 (timestamp, opt):
            start datetime for timestamp (intersecting / contained) filter
        timestamp2 (timestamp, opt):
            end datetime for timestamp (intersecting / contained) filter
        is_frequency(bool, opt, default=True):
            indicating if the frequency or performance visualization is selected
        attribute (str, opt):
            name of the attribute the attribute filter is applied on
        attribute_value (str, opt):
            the attribute value that is selected by the user
        operator (str, opt):
            a string operator sign out of [<=,>=,=,≠]

    ---
    Methods:
        set_attribute(): sets the attribute(s) of the filter
    """
    # string description of the filter type
    type = models.CharField(max_length=500, null=True, default=None)

    # for case-performance filter
    case_performance1 = models.IntegerField(null=True, default=None)
    case_performance2 = models.IntegerField(null=True, default=None)

    # for between filter
    case1 = models.CharField(max_length=500, null=True, default=None)
    case2 = models.CharField(max_length=500, null=True, default=None)

    # for case-size filter
    case_size1 = models.IntegerField(null=True, default=None)
    case_size2 = models.IntegerField(null=True, default=None)

    # for timestamp
    timestamp1 = models.DateTimeField(null=True)
    timestamp2 = models.DateTimeField(null=True)

    # frequency / performance
    is_frequency = models.BooleanField(default=True)

    # performance edge label
    edge_label = models.IntegerField(null=True)

    # attribute filter
    attribute = models.CharField(max_length=500, null=True)
    attribute_value = models.CharField(max_length=500, null=True)
    operator = models.CharField(max_length=500, null=True)

    def set_attribute(self, attr, value):
        """
        setter for filter attributes

        ---
        Params:
            attr:
                either a single string or a list of strings representing the attribute names
            value:
                either a single value or a list of values for each attribute
        """
        # if a list of keys is given, set each key to the corresponding
        # value key with key[index] = value[index]
        if isinstance(attr, list):
            for i, at in enumerate(attr):
                setattr(self, at, value[i])
        else:
            # since no list was given, just set the single attribute
            setattr(self, attr, value)


class LogObjectHandler(models.Model):
    """
    Handler for log object in comparison page

    ---
    Attributes:
        log_object:
            A :obj:`Log`
        filter (opt):
            The filter for the log
    """

    # a log model
    log_object = models.ForeignKey(Log,
                                   on_delete=models.CASCADE)

    # a filter (default or on delete None)
    filter = models.OneToOneField(Filter, null=True, on_delete=models.SET_NULL)

    def to_df(self):
        """converts log to df"""
        return log_to_data_frame.apply(self.pm4py_log())

    def get_activities(self):
        """returns all activites"""
        return pm4py.get_attribute_values(self.pm4py_log(), "concept:name")

    def get_properties(self):
        """returns properties of log"""
        log_df = self.to_df()
        results = {}

        for columName, columValue in log_df.iteritems():
            values_w_o_na = columValue.dropna()
            results[columName] = sorted(list(set(values_w_o_na)))
        return results

    def get_timestamps(self):
        """returns all timestamps"""
        return sorted(
            pm4py.get_attribute_values(
                self.pm4py_log(),
                "time:timestamp"))

    def get_similarity_index(self, reference):
        """
        Similarity Index based on the number of common variants between log and reference log
        """
        if reference and reference.generate_dfg(
                only_extract_filtered_log=True) != self.generate_dfg(
                only_extract_filtered_log=True):
            # Dictionary ('variant': 'count')of the log to be analyzed
            # 'count': number of occurrences per variant
            dict_variants_log = case_statistics.get_variant_statistics(
                self.generate_dfg(only_extract_filtered_log=True))
            # Dictionary of the reference log
            dict_variants_reference = case_statistics.get_variant_statistics(
                reference.generate_dfg(only_extract_filtered_log=True))

            # Total number of counts if both dictionaries have the similar variants
            sum_count_similar = 0
            # Iterate through the variants of the reference log dictionary
            for entry_reference in dict_variants_reference:
                # Iterate through the variants of the log dictionary
                for entry_log in dict_variants_log:
                    # Compare whether both dictionaries have the same variants
                    if entry_log['variant'] == entry_reference['variant']:
                        # Add the minimum number of identical variants (the intersection) to sum_count_similar
                        sum_count_similar += min(entry_log['count'],
                                                 entry_reference['count'])

            # Add the number of count values for each variant of the log
            sum_count_log = sum([entry_log['count']
                                for entry_log in dict_variants_log])
            # Add the number of count values for each variant of the reference log
            sum_count_reference = sum(
                [entry_reference['count'] for entry_reference in dict_variants_reference])

            # Return of the Similarity Index rounded to two decimal places
            return str("%.2f" % round(sum_count_similar/max(sum_count_log, sum_count_reference) * 100, 2)) + "%"
        # If log = reference log
        return "100%"

    def pm4py_log(self):
        """return parsed log"""
        return self.log_object.pm4py_log()

    def log_name(self):
        """return name of the log"""
        return self.log_object.log_name

    def generate_dfg(self, only_extract_filtered_log=False):
        """
        generates the dfg of the log

        ---
        Params:
            only_extract_filtered_log (bool, opt):
                optional bool to return the (filtered) log

        ---
        Returns:
            (filtered) dfg
                (if only_extract_filtered_log=False)
            (filtered) log
                 (if only_extract_filtered_log=True)
        """
        log = self.pm4py_log()
        # if a filter was selected
        if self.filter:
            # if something goes wrong while filtering,
            # (or there is a type error in the filter)
            # the filter is ignored
            filtered_log = None
            # 'switch' over implemeneted filters
            if self.filter.type == "case_performance":
                filtered_log = case_filter.filter_case_performance(
                    log, self.filter.case_performance1, self.filter.case_performance2)
            elif self.filter.type == "between_filter":
                filtered_log = pm4py.filter_between(
                    log, self.filter.case1, self.filter.case2)
            elif self.filter.type == "case_size":
                filtered_log = pm4py.filter_case_size(
                    log, self.filter.case_size1, self.filter.case_size2)
            elif self.filter.type == "timestamp_filter_contained":
                # normalize timestamps
                timestamp1, timestamp2 = make_naive(
                    self.filter.timestamp1, UTC), make_naive(
                    self.filter.timestamp2, UTC)
                filtered_log = timestamp_filter.filter_traces_contained(
                    log, timestamp1, timestamp2)
            elif self.filter.type == "timestamp_filter_intersecting":
                # normalize timestamps
                timestamp1, timestamp2 = make_naive(
                    self.filter.timestamp1, UTC), make_naive(
                    self.filter.timestamp2, UTC)
                filtered_log = timestamp_filter.filter_traces_intersecting(
                    log, timestamp1, timestamp2)
            elif self.filter.type == "filter_on_attributes":
                if self.filter.operator in ["<=", ">="]:
                    # if '<=' look at the range -inf to float(attribute_value)
                    # if '>=' look at the range float(attribute_value) to inf

                    # since '<=' and '>=' can only be selected for numeric attribute
                    # values, float(attribute_value) does not need to be
                    # try-catched
                    filtered_log = attributes_filter.apply_numeric(
                        log,
                        float('-inf') if self.filter.operator == "<="
                        else float(self.filter.attribute_value),
                        float(self.filter.attribute_value) if self.filter.operator == "<="
                        else float('inf'),
                        parameters={
                            attributes_filter.Parameters.ATTRIBUTE_KEY:
                            self.filter.attribute})
                else:
                    # operator is either '=' or '≠'
                    # check if the attribute value is a number
                    try:
                        value_float = float(self.filter.attribute_value)
                        value_int = int(value_float)
                        value = value_int if value_int == value_float else value_float 
                    except BaseException or ValueError:
                        value = self.filter.attribute_value
                    filtered_log = attributes_filter.apply(
                            log,
                            [value],
                            parameters={
                                attributes_filter.Parameters.ATTRIBUTE_KEY: self.filter.attribute,
                                attributes_filter.Parameters.POSITIVE: self.filter.operator == "="})
            # since the filtered log is only set if a filter was applied,
            # and thus not None, otherwise the filter is ignored
            if filtered_log is not None:
                log = filtered_log
        if only_extract_filtered_log:
            return log

        variant = dfg_discovery.Variants.FREQUENCY\
            if not self.filter or self.filter.is_frequency\
            else dfg_discovery.Variants.PERFORMANCE

        dfg = dfg_discovery.apply(log, variant=variant)
        return dfg

    def metrics(self, reference=None):
        """returns the metrics of a log or the comparison relative to the reference"""
        # get the global list of attributes
        global order
        # calculate the metrics for linked log
        # if a filter is applied, calculate the metrics for the filtered log
        metrics1 = LogMetrics(self.generate_dfg(
            only_extract_filtered_log=True))
        # if a reference was selected and the reference is different
        # to linked log, calulate the metrics for the reference
        # log as well and return the metrics of the linked log
        # and the difference relative to the reference log
        if reference and self.generate_dfg(
                only_extract_filtered_log=True) != reference.generate_dfg(
                only_extract_filtered_log=True):
            # if reference is filtered, calculate comparison for filtered
            metrics2 = LogMetrics(reference.generate_dfg(
                only_extract_filtered_log=True))
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
                        ), 1 if not self.filter or self.filter.is_frequency else self.filter.edge_label
                    ),
                    dfg_dict_to_g6(
                        convert_dfg_to_dict(
                            reference.generate_dfg()
                        ), 1 if not self.filter or self.filter.is_frequency else self.filter.edge_label
                    )
                )
            )
        return json.dumps(
            dfg_dict_to_g6(
                convert_dfg_to_dict(
                    self.generate_dfg()
                ), 1 if not self.filter or not self.filter.edge_label else self.filter.edge_label
            )
        )

    def reset_filter(self):
        if self.filter:
            Filter.objects.get(pk=self.filter_id).delete()
            self.filter = Filter.objects.create()

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

    def get_filter(self):
        """
        returns the filters applied to each log for the output within the PDF document
        """
        # if no filter is applied on the log
        # returns key "No filter selected"
        # returns value "No attribute(s) selected"
        if self.filter is None:
            return {"No filter selected": "No attribute(s) selected"}
        # if Case Performance Filter is applied on the log
        # returns key "Case Performance"
        # returns value concerning applied lower and upper limit 
        elif self.filter.type == "case_performance":
            return {"Case Performance": "Between " +
                    str(self.filter.case_performance1) +
                    " and " +
                    str(self.filter.case_performance2)}
        # if Between Filter is applied on the log
        # returns key "Between Filter"
        # returns value in terms of applied start and end activity 
        # the characters ' are used to highlight the two selected activities within the returned String
        elif self.filter.type == "between_filter":
            return {"Between Filter": "Between '" +
                    str(self.filter.case1) +
                    "' and '" +
                    str(self.filter.case2) +
                    "'"}
        # if Case Size Filter is applied on the log
        # returns key "Case Size"
        # returns value regarding applied lower and upper limit
        elif self.filter.type == "case_size":
            return {"Case Size": "Between " +
                    str(self.filter.case_size1) +
                    " and " +
                    str(self.filter.case_size2)}
        # if Timestamp Filter (Contanins) is applied on the log
        # returns key "Timestamp Filter (Contanins)"
        # returns value concerning applied start and end timestamp
        elif self.filter.type == "timestamp_filter_contained":
            return {
                "Timestamp Filter (contained)": "Between " +
                str(self.filter.timestamp1) +
                " and " +
                str(self.filter.timestamp2)}
        # if Timestamp Filter (Intersecting) is applied on the log
        # returns key "Timestamp Filter (Intersecting)"
        # returns value concerning applied start and end timestamp
        elif self.filter.type == "timestamp_filter_intersecting":
            return {
                "Timestamp Filter (intersecting)": "Between " +
                str(self.filter.timestamp1) +
                " and " +
                str(self.filter.timestamp2)}
        # if Filter on Attrbiutes is applied on the log
        # returns key "Filter on attributes"
        # returns value in terms of applied attribute filter type, operator and numeric attribute value
        elif self.filter.type == "filter_on_attributes":
            return {"Filter on attributes": self.filter.attribute + " " +
                    self.filter.operator + " " + str(self.filter.attribute_value)}


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

        # Number of Cases
        self.no_cases = len(self.log)

        # Number of Events
        self.no_events = sum([len(trace) for trace in self.log])

        # PM4Py library function
        variants_count = case_statistics.get_variant_statistics(log)
        
        # Number of Variants
        self.no_variants = len(variants_count)

        # PM4Py library function
        activities_count = pm4py.get_attribute_values(log, "concept:name")

        # Number of Activities
        self.no_activities = len(activities_count)

        # PM4Py library function
        all_case_durations = case_statistics.get_all_casedurations(
            self.log, parameters={
                case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"})
        
        # Total Case Duration
        self.total_case_duration = (sum(all_case_durations))

        # Average Case Duration
        if self.no_cases <= 0:
            avg_case_duration = 0
        else:
            avg_case_duration = (sum(all_case_durations)) / self.no_cases
        self.average_case_duration = avg_case_duration

        # PM4Py library function
        median_case_duration = (
            case_statistics.get_median_caseduration(
                self.log, parameters={
                    case_statistics.Parameters.TIMESTAMP_KEY: "time:timestamp"}))
        
        # Median Case Duration
        self.median_case_duration = median_case_duration
