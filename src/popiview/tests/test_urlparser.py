# coding=utf-8

import urlparse
import unittest
from popiview.urlparser import URLParser
from popiview.tests.base import TestBase

class TestURLParser(TestBase):

    def test_searchquery(self):
        """Test the detection of search query in referrer"""
        tests = []
        # Google query
        tests.append({
            'ref': u'http://google.nl?q=my query',
            'expect': (u'google.nl', u'my query')
        })
        # Yahoo query
        tests.append({
            'ref': u'http://yahoo.com?p=my query',
            'expect': (u'yahoo.com', u'my query')
        })
        # Query with extra querystring parameter before
        tests.append({
            'ref': u'http://google.nl/search?sourceid=chrome&q=my query',
            'expect': (u'google.nl', u'my query')
        })
        # Query with single quotes
        tests.append({
            'ref': u"http://google.nl?q='my query'",
            'expect': (u'google.nl', u"'my query'")
        })
        # Query with double quotes
        tests.append({
            'ref': u'http://google.nl?q="my query"',
            'expect': (u'google.nl', u'"my query"')
        })
        # Query with plus sign instead of space
        tests.append({
            'ref': u'http://google.nl?q=my+query',
            'expect': (u'google.nl', u'my query')
        })
        # Cyrillic characters
        tests.append({
            'ref': u'http://google.ru?q=русск альф',
            'expect': (u'google.ru', u'русск альф')
        })
        # No referrer
        tests.append({
            'ref': None,
            'expect': None 
        })
        # Not a search engine
        tests.append({
            'ref': u'http://www.example.com',
            'expect': None
        })
        # No query string
        tests.append({
            'ref': u'http://www.google.com',
            'expect': None
        })
        # Empty query string
        tests.append({
            'ref': u'http://www.google.com?q=',
            'expect': None
        })
        
        for test in tests:
            self.urlparser = URLParser(self._conf)
            ref = test['ref']
            if test['ref'] is not None:
                ref = list(urlparse.urlsplit(ref))
            self.assertEqual(self.urlparser.searchquery(ref), test['expect'])

    def test_keywords(self):
        """Test keyword separation from searchquery"""
        tests = []
        # Regular search
        tests.append({
            'query': 'test searchquery',
            'expect': ['test', u'searchquery']
        })
        # Number
        tests.append({
            'query': '123',
            'expect': ['123']
        })
        # Cyrillic characters
        tests.append({
            'query': u'русск альф',
            'expect': [u'русск', u'альф']
        })
        # Single quotes
        tests.append({
            'query': "my 'test query'",
            'expect': [u'my', u'test query']
        })
        # Double quotes
        tests.append({
            'query': 'my "test query"',
            'expect': [u'my', u'test query']
        })

        for test in tests:
            self.urlparser = URLParser(self._conf)
            ref = list(urlparse.urlsplit(u'http://google.com?q='+test['query']))
            self.assertEqual(self.urlparser.keywords(ref), test['expect'])

    def test_source(self):
        """Test source (referrer) type detection"""
        tests = []
        """# No referrer
        tests.append({
            'url': u'http://mysite.com/page',
            'ref': None,
            'expect': 'direct'
        })
        # Same domain
        tests.append({
            'url': u'http://mysite.com/page',
            'ref': u'http://mysite.com/anotherpage',
            'expect': 'internal'
        })
        # Another domain
        tests.append({
            'url': u'http://mysite.com/page',
            'ref': u'http://anothersite.com/page',
            'expect': u'external: anothersite.com'
        })"""
        # Same domain, different subdomain
        tests.append({
            'url': u'http://www.mysite.com/page',
            'ref': u'http://test.mysite.com/page',
            'expect': 'external: test.mysite.com'
        })
        # Search engine
        tests.append({
            'url': u'http://mysite.com/page',
            'ref': u'http://google.com?q=my "search query"',
            'expect': 'searches - google.com: my "search query"'
        })
        # Search engine, no query
        tests.append({
            'url': u'http://mysite.com/page',
            'ref': u'http://google.com',
            'expect': u'external: google.com'
        })
        # Search engine, empty query
        tests.append({
            'url': u'http://mysite.com/page',
            'ref': u'http://google.com?q=',
            'expect': u'external: google.com'
        })
        
        for test in tests:
            self.urlparser = URLParser(self._conf)
            url = test['url']
            if url is not None:
                url = list(urlparse.urlsplit(url))
            ref = test['ref']
            if ref is not None:
                ref = list(urlparse.urlsplit(ref))
            self.assertEqual(self.urlparser.source(url, ref), test['expect'])
 

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestURLParser))
    return suite
