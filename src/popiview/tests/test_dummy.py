# coding=utf-8

import unittest
import time
from popiview.dummy import Dummy
from popiview.tests.test_base import TestBase

class TestDummy(TestBase):
    
    def setUp(self):
        super(TestDummy, self).setUp()
        self.dummy = Dummy(self._conf, self._storage, clear=True)
    
    def test_create_linear_regular(self):
        """Test the linear creation of dummy hits - regular"""
        url = u'http://abc.nl/page'
        self.dummy.create_hits_linear(url,
            referrer=u'http://example.com/page?id=123',
            start_hits_per_hour=0, end_hits_per_hour=100,
            start_time=0, end_time=3600)
        hitcount = self._storage.get_hitcount(url)
        self.assertEqual(hitcount, 50)

    def test_create_linear_search(self):
        """Test the linear creation of dummy hits - searchengine"""
        url = u'http://abc.nl/page'
        self.dummy.create_hits_linear(url,
            referrer=u'http://google.com?q=my search query',
            start_hits_per_hour=0, end_hits_per_hour=100,
            start_time=0, end_time=3600)
        hitcount = self._storage.get_hitcount(url)
        self.assertEqual(hitcount, 50)

    def test_create_linear_cyrillic(self):
        """Test the linear creation of dummy hits - cyrillic"""
        url = u'http://abc.nl/page?x=миниатю'
        self.dummy.create_hits_linear(url,
            referrer=u'http://example.com/page/миниатю',
            start_hits_per_hour=0, end_hits_per_hour=100,
            start_time=0, end_time=3600)
        hitcount = self._storage.get_hitcount(url)
        self.assertEqual(hitcount, 50)

    def test_create_linear_no_timestamp(self):
        """Test the linear creation of dummy hits - no timestamp"""
        url = u'http://abc.nl/page'
        self.dummy.create_hits_linear(url,
            referrer=None,
            start_hits_per_hour=0, end_hits_per_hour=100,
            start_time=None, end_time=None)
        hitcount = self._storage.get_hitcount(url)
        self.assertEqual(hitcount, 1200)

    def test_create_linear_decreasing(self):
        """Test the linear creation of dummy hits - decreasing"""
        url = u'http://abc.nl/page'
        self.dummy.create_hits_linear(url,
            referrer=None,
            start_hits_per_hour=100, end_hits_per_hour=0,
            start_time=0, end_time=3600)
        hitcount = self._storage.get_hitcount(url)
        self.assertEqual(hitcount, 50)

    def test_create_linear_stable(self):
        """Test the linear creation of dummy hits - stable"""
        url = u'http://abc.nl/page'
        self.dummy.create_hits_linear(url,
            referrer=None,
            start_hits_per_hour=50, end_hits_per_hour=50,
            start_time=0,end_time=3600)
        hitcount = self._storage.get_hitcount(url)
        self.assertEqual(hitcount, 50)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDummy))
    return suite
