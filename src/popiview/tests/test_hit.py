# coding=utf-8

import unittest
from popiview.hit import Hit
from popiview.tests.test_base import TestBase

class TestHit(TestBase):

    def test_url_root(self):
        """Test the root url"""
        self.hit = Hit(self._conf, u'http://mysite.com')
        self.assertEqual(self.hit.url(), u'http://mysite.com')
        self.hit = Hit(self._conf, u'http://mysite.com/')
        self.assertEqual(self.hit.url(), u'http://mysite.com')

    def test_url_with_subdomain(self):
        """Test a url with a subdomain"""
        self.hit = Hit(self._conf, u'http://abc.mysite.com')
        self.assertEqual(self.hit.url(), u'http://abc.mysite.com')
    
    def test_url_with_ending_slash(self):
        """Test a url with an ending slash"""
        self.hit = Hit(self._conf, u'http://www.mysite.com/page')
        self.assertEqual(self.hit.url(), u'http://www.mysite.com/page')
        self.hit = Hit(self._conf, u'http://www.mysite.com/page/')
        self.assertEqual(self.hit.url(), u'http://www.mysite.com/page')

    def test_url_with_file_extension(self):
        """Test a url with a file extension"""
        self.hit = Hit(self._conf, u'http://mysite.com/page.html')
        self.assertEqual(self.hit.url(), u'http://mysite.com/page.html')

    def test_url_with_query_parameters(self):
        """Test a url with query string parameters and an anchor"""
        self.hit = Hit(self._conf, u'http://mysite.com/page?a=x&b=1#top')
        self.assertEqual(self.hit.url(), u'http://mysite.com/page?a=x&b=1#top')

    def test_url_with_cyrillic_chars(self):
        """Test a url with cyrillic (russian) characters in it"""
        self.hit = Hit(self._conf, u'http://mysite.com/page?a=русское альфа')
        self.assertEqual(self.hit.url(), 
            u'http://mysite.com/page?a=русское альфа')

    def test_url_non_unicode(self):
        """Test a url that is not provided as unicode string"""
        self.hit = Hit(self._conf, 'http://mysite.com/page?a=x&b=1#top')
        self.assertEqual(self.hit.url(), u'http://mysite.com/page?a=x&b=1#top')
    
    def test_path_with_subdomain(self):
        """Test a path with a subdomain"""
        self.hit = Hit(self._conf, u'http://www.mysite.com/page')
        self.assertEqual(self.hit.path(), u'/page')

    def test_path_with_file_extension(self):
        """Test a path with a file extension"""
        self.hit = Hit(self._conf, u'http://mysite.com/page.html')
        self.assertEqual(self.hit.path(), u'/page.html')

    def test_path_with_query_parameters(self):
        """Test a path with query string parameters and an anchor"""
        self.hit = Hit(self._conf, u'http://mysite.com/page?a=x&b=1#top')
        self.assertEqual(self.hit.path(), u'/page?a=x&b=1')

    def test_path_with_cyrillic_chars(self):
        """Test a path with cyrillic (russian) characters in it"""
        self.hit = Hit(self._conf, u'http://mysite.com/page?a=русское альфа')
        self.assertEqual(self.hit.path(), u'/page?a=русское альфа')

    def test_title_basic(self):
        """Test a title with basic characters"""
        self.hit = Hit(self._conf, u'http://abc.nl/page', 
                title='ABC.nl - Some random page')
        self.assertEqual(self.hit.title(), 'ABC.nl - Some random page')

    def test_title_specialchars(self):
        """Test a title with special characters"""
        self.hit = Hit(self._conf, u'http://abc.nl/page', 
                title='<>@!^#$%&*¶«{(?)}»~€⁂⁀®“『₳”"')
        self.assertEqual(self.hit.title(), 
                '<>@!^#$%&*¶«{(?)}»~€⁂⁀®“『₳”"')

    def test_title_cyrillic(self):
        """Test a title with cyrillic characters"""
        self.hit = Hit(self._conf, u'http://abc.nl/page',
                title='До последней, это до которой конкретно?')
        self.assertEqual(self.hit.title(),
                'До последней, это до которой конкретно?')

    def test_referrer_with_subdomain(self):
        """Test a referrer with a subdomain"""
        self.hit = Hit(self._conf, u'http://abc.nl/page',
                referrer=u'http://abc.xyz.nl/some/where')
        self.assertEqual(self.hit.referrer(), u'http://abc.xyz.nl/some/where')

    def test_referrer_with_file_extension(self):
        """Test a referrer with a file extension"""
        self.hit = Hit(self._conf, u'http://abc.nl/page',
                referrer=u'http://xyz.nl/page.html')
        self.assertEqual(self.hit.referrer(), u'http://xyz.nl/page.html')

    def test_referrer_with_query_parameters(self):
        """Test a referrer with query string parameters and an anchor"""
        self.hit = Hit(self._conf, u'http://abc.nl/page',
                referrer=u'http://xyz.nl/page?a=x&b=1#top')
        self.assertEqual(self.hit.referrer(), 
                u'http://xyz.nl/page?a=x&b=1#top')

    def test_referrer_with_cyrillic_chars(self):
        """Test a referrer with cyrillic (russian) characters in it"""
        self.hit = Hit(self._conf, u'http://abc.nl/page',
                referrer=u'http://xyz.nl/page?a=русское альфа')
        self.assertEqual(self.hit.referrer(), 
                u'http://xyz.nl/page?a=русское альфа')

    def test_timestamp(self):
        """Test the timestamp as (signed) int, string and None"""
        tests = []
        # Zero
        tests.append({'timestamp': 0, 'expect': 0})
        # Small number
        tests.append({'timestamp': 1000, 'expect': 1000})
        # Negative number
        tests.append({'timestamp': -1000, 'expect': -1000})
        # Regular size
        tests.append({'timestamp': 9879824154, 'expect': 9879824154 })
        # Big number
        tests.append({'timestamp': 98798241549879824154,
                      'expect': 98798241549879824154})
        # As a string
        tests.append({'timestamp': '-1000', 'expect': -1000})
        # None (fallback to current timestamp)
        tests.append({'timestamp': None, 'expect': self.now})

        for test in tests:
            self.hit = Hit(self._conf, u'http://abc.nl', 
                timestamp=test['timestamp'])
            self.assertEqual(self.hit.timestamp(), test['expect'])

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
            self.hit = Hit(self._conf, u'http://abc.nl', referrer=test['ref'])
            self.assertEqual(self.hit.searchquery(), test['expect'])

    def test_keywords(self):
        """Test keyword separation from searchquery, converted to lowercase"""
        tests = []
        # Regular search
        tests.append({
            'query': 'Test SearchQuery',
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
            self.hit = Hit(self._conf, u'http://abc.nl',
                referrer=u'http://google.com?q=' + test['query'])
            self.assertEqual(self.hit.keywords(), test['expect'])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHit))
    return suite
