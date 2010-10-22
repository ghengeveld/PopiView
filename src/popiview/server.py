import json
import random
import mimetypes
from webob import Request, Response
from popiview.hit import Hit
from popiview.storage import MemoryStorage, SQLStorage
from popiview.analyzer import Analyzer
from popiview.dummy import Dummy
from popiview.view import View

class PopiWSGIServer(object):
    
    def __init__(self, storage):
        self._storage = storage
        self._deviation_analyzer = Analyzer(self._storage)
        self._keyword_analyzer = Analyzer(self._storage)
        self._view = View()
        self._image = self.load_component('img/img.gif')

    def index(self):
        view = self._view.index()
        return Response(view)
    
    def cleardata(self):
        self._storage.clear_hits()
        return Response('done')

    def deviators(self):
        output = self._deviation_analyzer.get_top_deviators()
        return Response(json.dumps(output))
    
    def keywordcloud(self):
        output = self._keyword_analyzer.get_keyword_cloud(minimum_pct=80,
                                                          maximum_pct=500)
        return Response(json.dumps(output))

    def hitmonitor(self):
        last_timestamp = int(self.request.GET.get('last_timestamp', 0))
        sources = {'ext': int(self.request.GET.get('ext', 1)), 
                   'sea': int(self.request.GET.get('sea', 1)),
                   'int': int(self.request.GET.get('int', 1)),
                   'dir': int(self.request.GET.get('dir', 1))}
        output = self._storage.get_recenthits(sources, last_timestamp + 1)
        return Response(json.dumps(output))

    def dummydata(self):
        dummy = Dummy(self._storage, True)

        dummy.create_hits_linear(u'http://www.mysite.com/page',
                                 start_time=0, end_time=10000,
                                 start_hits_per_hour=0, end_hits_per_hour=50,
                                 referrer='http://google.com?q=cool%20page')
        dummy.create_hits_linear(u'http://www.mysite.com/page',
                                 start_time=5000, end_time=10000,
                                 start_hits_per_hour=0, end_hits_per_hour=50,
                                 referrer='http://www.google.com?q=cool')
        dummy.create_hits_linear(u'http://www.mysite.com/page2',
                                 start_time=0, end_time=10000,
                                 start_hits_per_hour=20, end_hits_per_hour=80)
        dummy.create_hits_linear(u'http://www.mysite.com/page3',
                                 start_time=0, end_time=10000,
                                 start_hits_per_hour=0, end_hits_per_hour=75)
        dummy.create_hits_linear(u'http://www.mysite.com/page4',
                                 start_time=0, end_time=10000,
                                 start_hits_per_hour=200, end_hits_per_hour=0)
        
        rand_start = random.random() * 60
        rand_end = random.random() * 60
        dummy.create_hits_linear(u'http://www.mysite.com/page2',
                                 start_time=0, end_time=10000,
                                 start_hits_per_hour=rand_start, 
                                 end_hits_per_hour=rand_end,
                                 referrer='http://www.google.com?q=page2')
        return Response('done')

    def randomdata(self):
        dummy = Dummy(self._storage)
        rand = int(random.random() * 10) + 1
        for i in range(rand):
            rand_start = random.random() * 60
            rand_end = random.random() * 60
            dummy.create_hits_linear(
                u'http://www.mysite.com/page' + str(rand),
                start_hits_per_hour=rand_start, end_hits_per_hour=rand_end,
                referrer='http://www.google.com?q=page' + str(rand))
        return Response('done')

    def log_hit(self):
        cur = self.request.GET.get('cur', None)
        ref = self.request.GET.get('ref', None)
        title = self.request.GET.get('title', None)

        if cur is None:
            cur = self.request.headers.get('referer', None)

        response = Response()
        response.headers['Content-Type'] = "image/gif"
        response.headers['Expires'] = "Sat, 26 Jul 1997 05:00:00 GMT"
        response.headers['Cache-Control'] = "no-cache, must-revalidate"
        response.body = self._image

        if cur is not None:
            hit = Hit(cur, referrer=ref, title=title)
            self._storage.add_hit(hit)
	    return response

    def load_component(self, filepath):
        with open('components/' + filepath) as f:
            data = f.read()
        return data

    def get_component(self):
        filepath = self.request.GET.get('file', None)
        mimetype = mimetypes.guess_type(filepath, False)
        response = Response()
        response.headers['Content-Type'] = mimetype[0]
        response.body = self.load_component(filepath)
        return response 

    def __call__(self, environ, start_response):
        self.request = Request(environ)
        urlmap = local_conf['urlmap']
        name = self.request.path_info_pop()
        if name == '':
            name = 'index'
        method_name = urlmap.get(name, None)
        if method_name:
            method = getattr(self, method_name, None)
        if method_name is None or method is None:
            response = Response('Not Found')
            response.status = 404
        else:
            response = method()
        return response(environ, start_response)


def app_factory(global_config, storage_name, **local_conf):
    global local_conf
    if storage_name == 'memory':
        storage = MemoryStorage()
    elif storage_name == 'sql':
        storage = SQLStorage(
            dbhost = local_conf['dbhost'],
            dbuser = local_conf['dbuser'],
            dbpass = local_conf['dbpass'],
            dbname = local_conf['dbname']
        )
    else:
        raise ValueError('No such storage: %s' % storage_name)
    return PopiWSGIServer(storage)
