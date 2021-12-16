import unittest
from django.test import TestCase
from logs.models import Log, LogObjectHandler, LogMetrics, Filter
from django.core.files.base import ContentFile
from secrets import token_bytes, token_hex

class LogTestCase(TestCase):
    def setUp(self):
        sample_log = ContentFile(token_bytes(5), token_hex(5))
        Log.objects.create(log_file=sample_log, log_name="test1")
        Log.objects.create(log_file=sample_log, log_name="test2")

    def test_log_eq(self):
        '''Logs with different names but same log file'''
        test1, test2 = Log.objects.all()
        self.assertNotEqual(test1.pk, test2.pk)
        self.assertNotEqual(test1.log_name, test2.log_name)
        self.assertEqual(test1, test2)
        
class LogObjectHandlerTestCase(TestCase):
    def setUp(self):
        sample_log = ContentFile(token_bytes(5), "test_log_name")
        log = Log.objects.create(log_file=sample_log, log_name=sample_log.name)
        LogObjectHandler.objects.create(log_object=log)

    def test_handler_filter(self):
        log = Log.objects.get(log_name="test_log_name")
        handler = LogObjectHandler.objects.get(log_object=log)
        self.assertEqual(handler.filter, None)
        handler.set_filter("test","")
        self.assertNotEqual(handler.filter, None)
        var1 = handler.filter.test
        handler.set_filter("test", " ")
        self.assertNotEqual(var1, handler.filter.test)
        Filter.objects.get(pk=handler.filter_id).delete()
        handler = LogObjectHandler.objects.get(log_object=log)
        self.assertEqual(handler.filter, None)



class LogMetricsTestCase(TestCase):
    pass

