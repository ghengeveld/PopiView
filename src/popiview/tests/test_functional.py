import unittest

from webob import Request
from popiview.server import PopiWSGIServer
from popiview.tests.test_base import TestBase


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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFunctional))
    return suite
