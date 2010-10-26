import unittest

class TestBase(unittest.TestCase):

    def setUp(self):
        config = {'sparams': {'bing': 'q', 'google': 'q', 'yahoo': 'p'}, 
                  'dbhost': 'localhost', 'dbpass': 'qqrs', 'urlmap': 
                  {'index': 'index', 'keywordcloud.json': 'keywordcloud', 
                   'cleardata': 'cleardata', 'component': 'get_component', 
                   'hitmonitor.json': 'hitmonitor', 'randomdata': 'randomdata', 
                   'deviators.json': 'deviators', 'image.gif': 'log_hit',
                   'dummydata': 'dummydata'
                  }, 'dbuser': 'root', 'dbname': 'popiview'}
        self._conf = config

    def tearDown(self):
        pass
