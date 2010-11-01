# coding=utf-8

import unittest
import time
from popiview.dummy import Dummy
from popiview.analyzer import Analyzer
from popiview.hit import Hit
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

    def test_keywordcloud_basic(self):
        """Test generation of keyword cloud - basic"""
        tests = []
        # Regular search
        tests.append({
            'ref': u'http://google.com?q=cool page', 
            'expect': [('cool', 50.0, [u'cool page']), 
                       ('page', 50.0, [u'cool page'])]
        })
        # Empty search query
        tests.append({
            'ref': u'http://google.com?q=', 
            'expect': []
        })
        # No search query
        tests.append({
            'ref': u'http://google.com', 
            'expect': []
        })
        # With query, but no searchengine
        tests.append({
            'ref': u'http://mysite.com?q=test', 
            'expect': []
        })

        for test in tests:
            self._storage.clear_hits()
            hit = Hit(self._conf, u'http://mysite.com/page',
                      referrer=test['ref'])
            self._storage.add_hit(hit)
            self.assertEqual(self.analyzer.get_keyword_cloud(), test['expect'])
    
    def test_keywordcloud_multi(self):
        """Test generation of keyword cloud - multiple hits"""
        searches = [
            'cool page',
            'funny test',
            'cool',
            'page',
            'cool',
            'test page test',
            'cool test page',
            'page',
            'cool page',
            'very cool funny test page'
        ]
        
        for query in searches:
            hit = Hit(self._conf, u'http://mysite.com/page',
                      referrer=u'http://google.com?q='+query)
            self._storage.add_hit(hit)

        self.assertEqual(sorted(self.analyzer.get_keyword_cloud()), 
            sorted([
                ('cool', 30.0, sorted([u'cool page', u'cool', u'cool test page',
                    u'very cool funny test page'])),
                ('page', 35.0, sorted([u'cool page', u'page', u'test page test',
                    u'cool test page', u'very cool funny test page'])),
                ('funny', 10.0, sorted([u'funny test',
                    u'very cool funny test page'])),
                ('test', 20.0, sorted([u'funny test', u'test page test', 
                    u'cool test page', u'very cool funny test page'])),
                ('very', 5.0, sorted([u'very cool funny test page']))
            ]))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAnalyzer))
    return suite
