import unittest
from popiview.hit import Hit
from popiview.tests.test_base import TestBase

class TestHit(TestBase):

    def test_url_with_subdomain(self):
        """Test a url with a subdomain"""
        self.hit = Hit(self._conf, u'http://www.mysite.com/page')
        self.assertEqual(self.hit.url(), 'http://www.mysite.com/page')

    def test_url_with_file_extension(self):
        """Test a url with a file extension"""
        self.hit = Hit(self._conf, u'http://mysite.com/page.html')
        self.assertEqual(self.hit.url(), 'http://mysite.com/page.html')

    def test_url_with_query_parameters(self):
        """Test a url with query string parameters and an anchor"""
        self.hit = Hit(self._conf, u'http://mysite.com/page?a=x&b=1#top')
        self.assertEqual(self.hit.url(), 'http://mysite.com/page?a=x&b=1#top')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHit))
    return suite
