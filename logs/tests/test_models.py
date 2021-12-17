import unittest
from django.test import TestCase
from logs.models import Log, LogObjectHandler, LogMetrics, Filter
from django.core.files.base import ContentFile
from secrets import token_bytes, token_hex

class ModelsLogTests(TestCase):
    def setUp(self):
        sample_log = ContentFile(token_bytes(5), token_hex(5))
        Log.objects.create(log_file=sample_log, log_name="test1")
        Log.objects.create(log_file=sample_log, log_name="test2")

    def test_log_eq(self):
        '''Logs with different names but same log file'''
        log1, log2 = Log.objects.all()
        self.assertNotEqual(log1.pk, log2.pk)
        self.assertNotEqual(log1.log_name, log2.log_name)
        self.assertEqual(log1, log2)
        
class ModelsLogObjectHandlerTests(TestCase):
    def setUp(self):
        sample_log = ContentFile(token_bytes(5), "test_log_name")
        log = Log.objects.create(log_file=sample_log, log_name=sample_log.name)
        LogObjectHandler.objects.create(log_object=log)

    def test_handler_log(self):
        '''test the associated log file'''
        handler = LogObjectHandler.objects.get(pk=1)
        log = Log.objects.get(pk=1)
        self.assertEqual(handler.log_object, log)

    def test_handler_filter_creation(self):
        '''test filter creation'''
        handler = LogObjectHandler.objects.get(pk=1)
        self.assertIsNone(handler.filter)
        handler.set_filter(" ", "")
        self.assertIsNotNone(handler.filter)

    # ...