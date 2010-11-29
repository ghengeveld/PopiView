import unittest
import time
from popiview.storage import SQLStorage

class TestBase(unittest.TestCase):

    def setUp(self):
        config = {'sparams': {'bing': 'q', 'google': 'q', 'yahoo': 'p'},
                  'urlmap': {
                    'index': 'index', 'keywordcloud.json': 'keywordcloud',
                    'cleardata': 'cleardata', 'component': 'get_component',
                    'hitmonitor.json': 'hitmonitor',
                    'randomdata': 'randomdata', 'dummydata': 'dummydata',
                    'deviators.json': 'deviators', 'image.gif': 'log_hit'},
                  'dbtype': 'sqlite',
                  'dbfile': ':memory:',
                  'dbhost': 'localhost',
                  'dbuser': 'root',
                  'dbpass': 'qqrs',
                  'dbname': 'popiview',
                  'recenthits_size': '200',
                  'title_strip': '| brusselnieuws.be',
                  'whitelist_lvl1': '',
                  'keyword_ignorelist': 'brussel, nieuws',
                 }
        self._conf = config
        self._storage = SQLStorage(config)
        self._storage._setup()
        self.now = int(time.time())

    def tearDown(self):
        self._storage._close_connection()
