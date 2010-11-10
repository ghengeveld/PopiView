# coding=utf-8

import unittest

from webob import Request
from popiview.server import PopiWSGIServer
from popiview.tests.test_base import TestBase
from urllib import quote


class TestFunctional(TestBase):

    def setUp(self):
        super(TestFunctional, self).setUp()
        self.app = PopiWSGIServer(self._conf, self._storage)

    def test_image_without_paramaters(self):
        """ Test image.gif without javascript inserted parameters """
        request = Request.blank('/image.gif')
        response = request.get_response(self.app)
        self.assertEquals('200 OK', response.status)
        expected_headers = {'Content-Length': '807',
                            'Expires': 'Sat, 26 Jul 1997 05:00:00 GMT',
                            'Content-Type': 'image/gif',
                            'Cache-Control': 'no-cache, must-revalidate'}
        self.assertEquals(expected_headers, dict(response.headers))

    def test_latin1(self):
        """Test latin-1 encoding in request"""
        request = Request.blank(
            '/image.gif?cur=' + quote('http://mysite.com/dead')
            + '&ref='
            + quote('http://google.com?q='+ quote(u'café'.encode('latin1')))
            + '&title=sometitle')

        for i in range(1,1000):
            response = request.get_response(self.app)
        self.assertEquals('200 OK', response.status)
        request = Request.blank('/keywordcloud.json')
        response = request.get_response(self.app)
        self.assertEquals('200 OK', response.status)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFunctional))
    return suite
