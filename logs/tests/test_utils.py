import unittest
from django.test import TestCase
from logs.utils import get_difference, days_hours_minutes, get_difference_days_hrs_min, find_node_in_g6, highlight_nonstandard_activities


class UtilsGetDifferenceTests(TestCase):
    def test_difference_res1_greater_res2(self):
        res1, res2 = 50, 10
        self.assertEqual(get_difference(res1, res2), [res1, f"+{res1-res2}"])

    def test_difference_res1_smaller_res2(self):
        res1, res2 = 10, 50
        self.assertEqual(get_difference(res1, res2), [res1, str(res1 - res2)])

    def test_difference_res1_equal_res2(self):
        res1 = res2 = 10
        self.assertEqual(get_difference(res1, res2), [res1, "0"])


class UtilsDaysHoursMinutesTests(TestCase):
    def test_date_conversion(self):
        self.assertEqual(days_hours_minutes(432000), "5d 0h 0m 0s")

    def test_date_zero(self):
        self.assertEqual(days_hours_minutes(0), "0d 0h 0m 0s")


class UtilsGetDifferenceDaysHoursMinutesTests(TestCase):
    def test_difference_d_h_m_res1_greater_res2(self):
        res1, res2 = 50, 10
        self.assertEqual(
            get_difference_days_hrs_min(
                res1, res2), [
                "0d 0h 0m 50s", "+0d 0h 0m 40s"])

    def test_difference_d_h_m_res1_smaller_res2(self):
        res1, res2 = 10, 50
        self.assertEqual(
            get_difference_days_hrs_min(
                res1, res2), [
                "0d 0h 0m 10s", "-1d 23h 59m 20s"])

    def test_difference_d_h_m_res1_equal_res2(self):
        res1 = res2 = 50
        self.assertEqual(
            get_difference_days_hrs_min(
                res1, res2), [
                "0d 0h 0m 50s", "0d"])


class UtilsFindNodeInG6Tests(TestCase):
    def test_find_node_in_g6_true(self):
        reference = {'nodes': [{'name': 'test1'}, {'name': 'test2'}]}
        name = "test1"
        self.assertTrue(find_node_in_g6(name, reference))

    def test_find_node_in_g6_false(self):
        reference = {'nodes': [{'name': 'test1'}, {'name': 'test2'}]}
        name = "test3"
        self.assertFalse(find_node_in_g6(name, reference))


class UtilsHighlightNonStandardActivitiesTests(TestCase):
    def test_highlight_non_standard_activities_equal(self):
        graph1 = graph2 = {'nodes': [{'name': 'test1'}]}
        highlight_nonstandard_activities(graph1, graph2)
        self.assertEqual(graph1, graph2)

    def test_highlight_nonstandard_activities_not_equal(self):
        graph1 = {'nodes': [{'name': 'test1'}, {'name': 'test2'}]}
        graph2 = {'nodes': [{'name': 'test1'}]}
        highlight_nonstandard_activities(graph1, graph2)
        self.assertEqual(graph1['nodes'][0]['isUnique'], 'False')
        self.assertEqual(graph1['nodes'][1]['isUnique'], 'True')
