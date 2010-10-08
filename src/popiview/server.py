import json
import random
from webob import Request, Response
from popiview.hit import Hit
from popiview.storage import MemoryStorage
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


    def index(self):
        view = self._view.index()
        return Response(view)


    def deviators(self):
        output = self._deviation_analyzer.get_top_deviators()
        return Response(json.dumps(output))

    
    def keywordcloud(self):
        output = self._keyword_analyzer.get_keyword_cloud()
        return Response(json.dumps(output))


    def hitmonitor(self):
        output = self._storage.get_recenthits()
        return Response(json.dumps(output))


    def dummydata(self):
        dummy = Dummy(self._storage)

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


    def image_gif(self):
        cur = self.request.GET['cur']
        ref = self.request.GET['ref']

        response = Response()
        response.headers['Content-Type'] = "image/gif"
        response.headers['Expires'] = "Sat, 26 Jul 1997 05:00:00 GMT"
        response.headers['Cache-Control'] = "no-cache, must-revalidate"
        response.body = load_image()

        hit = Hit(cur, ref)
        self.storage.add_hit(hit)
	
        return response


    def __call__(self, environ, start_response):
        self.request = Request(environ)
        name = self.request.path_info_pop()
        method_name = self._urlmap.get(name, None)
        method = getattr(self, method_name, None)
        if method is None:
            response = Response('Not Found')
            response.status = 404
        else:
            response = method()
        return response(environ, start_response)


def app_factory(global_config, storage_name, urlmap, **local_conf):
    if storage_name == 'memory':
        storage = MemoryStorage()
    else:
        raise ValueError('No such storage: %s' % storage_name)
    return PopiWSGIServer(storage, urlmap)
