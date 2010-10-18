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
    
    def __init__(self, storage, urlmap):
        self._storage = storage
        self._urlmap = urlmap
        self._deviation_analyzer = Analyzer(self._storage, start_time=0,
                                            boundary_time=7000, end_time=10000)
        self._keyword_analyzer = Analyzer(self._storage, start_time=0,
                                          boundary_time=7000, end_time=10000)
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
        output = self._keyword_analyzer.get_keyword_cloud(minimum_pct=25, 
                                                          maximum_pct=300)
        return Response(json.dumps(output))

    def hitmonitor(self):
        output = self._storage.get_recenthits()
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

        if cur is None:
            cur = self.request.headers.get('referer', None)

        response = Response()
        response.headers['Content-Type'] = "image/gif"
        response.headers['Expires'] = "Sat, 26 Jul 1997 05:00:00 GMT"
        response.headers['Cache-Control'] = "no-cache, must-revalidate"
        response.body = self._image

        if cur is not None:
            hit = Hit(cur, referrer=ref)
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
        name = self.request.path_info_pop()
        if name == '':
            name = 'index'
        method_name = self._urlmap.get(name, None)
        method = getattr(self, method_name, None)
        if method is None:
            response = Response('Not Found')
            response.status = 404
        else:
            response = method()
        return response(environ, start_response)


def app_factory(global_config, storage_name, **local_conf):
    if storage_name == 'memory':
        storage = MemoryStorage()
    elif storage_name == 'sql':
        storage = SQLStorage()
    else:
        raise ValueError('No such storage: %s' % storage_name)
    urlmap = {}
    for key, value in local_conf.iteritems():
        if key.startswith('urlmap'):
            k = key.split('.', 1)[1]
            urlmap[k] = value
    return PopiWSGIServer(storage, urlmap)
