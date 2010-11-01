# coding=utf-8

import unittest
import time
from popiview.dummy import Dummy
from popiview.analyzer import Analyzer
from popiview.tests.test_base import TestBase

class TestAnalyzer(TestBase):

    def setUp(self):
        super(TestAnalyzer, self).setUp()
        self.analyzer = Analyzer(self._storage, 
            start_time=0, boundary_time=7500, end_time=10000)
        self.dummy = Dummy(self._conf, self._storage, clear=True)
    
    def test_deviators_stable(self):
        """Test listing of top deviators - stable"""
        self.dummy.create_hits_linear(u'http://mysite.com/page1',
            start_hits_per_hour=5000, end_hits_per_hour=5000,
            start_time=0, end_time=10000)
        self.assertEqual(self.analyzer.get_top_deviators(qfield='hit_url'), 
            [{'name': u'http://mysite.com/page1', 'value': 0}])
    
    def test_deviators_increasing(self):
        """Test listing of top deviators - increasing"""
        self.dummy.create_hits_linear(u'http://mysite.com/page2',
            start_hits_per_hour=0, end_hits_per_hour=8000,
            start_time=0, end_time=10000)
        self.assertEqual(self.analyzer.get_top_deviators(qfield='hit_url'), 
            [{'name': u'http://mysite.com/page2', 'value': 133}])
    
    def test_deviators_decreasing(self):
        """Test listing of top deviators - decreasing"""
        self.dummy.create_hits_linear(u'http://mysite.com/page3',
            start_hits_per_hour=8000, end_hits_per_hour=0,
            start_time=0, end_time=10000)
        self.assertEqual(self.analyzer.get_top_deviators(qfield='hit_url'), 
            [{'name': u'http://mysite.com/page3', 'value': -80}])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAnalyzer))
    return suite
