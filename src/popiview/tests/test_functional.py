# coding=utf-8

import unittest
import json
from webob import Request
from popiview.server import PopiWSGIServer
from popiview.tests.base import TestBase
from urllib import quote_plus

class TestFunctional(TestBase):

    def setUp(self):
        super(TestFunctional, self).setUp()
        self.app = PopiWSGIServer(self._conf, self._storage)

    def test_image_basic(self):
        """Test image.gif with only required parameters"""
        request = Request.blank('/image.gif?cur=http%3A%2F%2Fwww.mysite.com')
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        request = Request.blank('/keywordcloud.json')
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        self.assertEqual([], json.loads(response.body))
        
    def test_image_searchquery(self):
        """Test image.gif with searchengine as referrer"""
        request = Request.blank('/image.gif?cur='
                + quote_plus('http://www.mysite.com/page')
                + '&ref='
                + quote_plus('http://www.google.com?q=café')
                + '&title=Google'
            ) 
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        request = Request.blank('/keywordcloud.json')
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        self.assertEqual([[u'café', 500.0]], json.loads(response.body))

    def test_image_without_params(self):
        """Test image.gif without javascript inserted parameters"""
        request = Request.blank('/image.gif')
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        request = Request.blank('/keywordcloud.json')
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        self.assertEqual([], json.loads(response.body))
    
    def test_image_utf8(self):
        """Test image.gif with utf-8 encoding in request"""
        request = Request.blank('/image.gif?cur='
                + quote_plus(u'http://www.mysite.com/page'.encode('utf8'))
                + '&ref='
                + quote_plus(u'http://www.google.com?q=café'.encode('utf8'))
                + '&title=Google'
            ) 
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        request = Request.blank('/keywordcloud.json')
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        self.assertEqual([[u'café', 500.0]], json.loads(response.body))

    def test_image_latin1(self):
        """Test image.gif with latin-1 encoding in request"""
        request = Request.blank('/image.gif?cur='
                + quote_plus(u'http://www.mysite.com/page'.encode('latin1'))
                + '&ref='
                + quote_plus(u'http://www.google.com?q=café'.encode('latin1'))
                + '&title=Google'
            ) 
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        request = Request.blank('/keywordcloud.json')
        response = request.get_response(self.app)
        self.assertEqual('200 OK', response.status)
        self.assertEqual([[u'café', 500.0]], json.loads(response.body))

    def tearDown(self):
        super(TestFunctional, self).tearDown()
        self.app = None

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFunctional))
    return suite
