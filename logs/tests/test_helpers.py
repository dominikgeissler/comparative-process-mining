from helpers.dfg_helper import convert_dfg_to_dict
from helpers.g6_helpers import highlight_nonstandard_activities, dfg_dict_to_g6
from helpers.metrics_helper import get_difference_days_hrs_min, get_difference, days_hours_minutes

from django.test import TestCase

class ConvertDFGToDictTestCase(TestCase):
    pass

class HighlightNonStandardActivitiesTestCase(TestCase):
    pass

class ConvertDFGToG6TestCase(TestCase):
    pass

class DaysHoursMinutesTestCase(TestCase):
    def setUp(self):
        '''
        total_seconds, expected return
        '''
        self.testCases = [
            [0, "0d 0h 0m 0s"],
            [432000, "5d 0h 0m 0s"],
            [5000000, "57d 20h 53m 20s"]
        ]

    def test_days_hours_minutes(self):
        for test in self.testCases:
            returnVal = days_hours_minutes(test[0])
            self.assertEqual(returnVal, test[1])

class GetDifferenceDaysHoursMinutesTestCase(TestCase):
    def setUp(self):
        '''
        res1, res2, expected return
        input in seconds (res1, res2)
        output as formatted date string
        '''
        self.testCases = [
            [432000, 0, ["5d 0h 0m 0s", "+5d 0h 0m 0s"]],   # test two values (res1 > res2)
            [0, 0, ["0d 0h 0m 0s", "0d"]],                  # test same value (res1 = res2)
            [0, 432000, ["0d 0h 0m 0s", "-5d 0h 0m 0s"]]    # test two values (res1 < res2)
        ]

    def test_get_difference_days_hours_minutes(self):
        for test in self.testCases:
            returnVal = get_difference_days_hrs_min(test[0], test[1])
            self.assertEqual(returnVal, test[2])

class GetDifferenceTestCase(TestCase):
    def setUp(self):
        '''
        res1, res2, expected return
        '''
        self.testCases = [
            [100,50,[100, "+50"]],  # test two values (res1 > res2)
            [100,100, [100, "0"]],  # test same value (res1 = res2)
            [50, 100, [50, "-50"]]  # test two values (res1 < res2) 
            ]

    def test_get_difference(self):
        for test in self.testCases:
            returnVal = get_difference(test[0], test[1])
            self.assertEqual(returnVal, test[2])
