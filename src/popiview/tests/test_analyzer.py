# coding=utf-8

import unittest
import time
from popiview.dummy import Dummy
from popiview.analyzer import Analyzer
from popiview.hit import Hit
from popiview.tests.base import TestBase

class TestAnalyzer(TestBase):

    def setUp(self):
        super(TestAnalyzer, self).setUp()
        self.analyzer = Analyzer(self._storage)
        self.dummy = Dummy(self._conf, self._storage, clear=True)
    
    def test_deviators_stable(self):
        """Test listing of top deviators - stable"""
        self.dummy.create_hits_linear(u'http://mysite.com/page1',
            start_hits_per_hour=5000, end_hits_per_hour=5000,
            start_time=0, end_time=10000)
        self.assertEqual(self.analyzer.get_top_deviators(qfield='hit_url', 
            start_time=0, boundary_time=7500, end_time=10000), 
            [{'name': u'http://mysite.com/page1', 'pct': 0, 
                'hph_recent': 5001, 'hph_historic': 4999,
                'num_recent': 3473, 'num_historic': 10416}])
    
    def test_deviators_increasing(self):
        """Test listing of top deviators - increasing"""
        self.dummy.create_hits_linear(u'http://mysite.com/page2',
            start_hits_per_hour=0, end_hits_per_hour=8000,
            start_time=0, end_time=10000)
        self.assertEqual(self.analyzer.get_top_deviators(qfield='hit_url', 
            start_time=0, boundary_time=7500, end_time=10000), 
            [{'name': u'http://mysite.com/page2', 'pct': 133, 
                'hph_recent': 6999, 'hph_historic': 2999,
                'num_recent': 4861, 'num_historic': 6249}])
    
    def test_deviators_decreasing(self):
        """Test listing of top deviators - decreasing"""
        self.dummy.create_hits_linear(u'http://mysite.com/page3',
            start_hits_per_hour=8000, end_hits_per_hour=0,
            start_time=0, end_time=10000)
        self.assertEqual(self.analyzer.get_top_deviators(qfield='hit_url', 
            start_time=0, boundary_time=7500, end_time=10000), 
            [{'name': u'http://mysite.com/page3', 'pct': -80, 
                'hph_recent': 1000, 'hph_historic': 5000,
                'num_recent': 695, 'num_historic': 10417}])

    def test_toppages_basic(self):
        """Test listing of top pages - basic"""
        self.dummy.create_hits_linear(u'http://mysite.com/page',
            start_hits_per_hour=50, end_hits_per_hour=50,
            start_time=0, end_time=3600)
        self.assertEqual(self.analyzer.get_top_pages(qfield='hit_url',
            start_time=0, end_time=3600), [
                {'name': u'http://mysite.com/page', 'count': 50, 'hph': 50.0}
            ])

    def test_toppages_strings(self):
        """Test listing of top pages - timestamps as string"""
        self.dummy.create_hits_linear(u'http://mysite.com/page',
            start_hits_per_hour=50, end_hits_per_hour=50,
            start_time=0, end_time=3600)
        self.assertEqual(self.analyzer.get_top_pages(qfield='hit_url',
            start_time='0', end_time='3600'), [
                {'name': u'http://mysite.com/page', 'count': 50, 'hph': 50.0}
            ])
    
    def test_toppages_timespan(self):
        """Test listing of top pages - using timespan"""
        self.dummy.create_hits_linear(u'http://mysite.com/page',
            start_hits_per_hour=50, end_hits_per_hour=50,
            start_time=time.time() - 3600, end_time=time.time())
        self.assertEqual(self.analyzer.get_top_pages(qfield='hit_url',
            timespan='3600'), [
                {'name': u'http://mysite.com/page', 'count': 50, 'hph': 50.0}
            ])
    
    def test_keywordcloud_basic(self):
        """Test generation of keyword cloud - basic"""
        tests = []
        # Regular search
        tests.append({
            'ref': u'http://google.com?q=cool page', 
            'expect': [('cool', 50.0), ('page', 50.0)]
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
                ('cool', 30.0), ('page', 35.0), ('funny', 10.0),
                ('test', 20.0), ('very', 5.0)
            ]))

    def test_keywordcloud_specialchars(self):
        """Test generation of keyword cloud - special characters"""
        hit = Hit(self._conf, u'http://mysite.com/page',
            referrer=u'http://google.com?q=éäüòñрусском')
        self._storage.add_hit(hit)
        self.assertEqual(self.analyzer.get_keyword_cloud(), 
            [(u'éäüòñрусском', 100.0)])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAnalyzer))
    return suite
