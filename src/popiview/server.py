import json
import random
import mimetypes
import urllib
from webob import Request, Response
from popiview.hit import Hit
from popiview.storage import MemoryStorage, SQLStorage
from popiview.analyzer import Analyzer
from popiview.dummy import Dummy
from popiview.view import View

class PopiWSGIServer(object):
    
    def __init__(self, config, storage):
        self._conf = config
        self._storage = storage
        self._deviation_analyzer = Analyzer(self._storage)
        self._keyword_analyzer = Analyzer(self._storage)
        self._view = View()
        self._image = self._load_component('img/img.gif')

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
        sources = {'external': int(self.request.GET.get('ext', 1)), 
                   'searches': int(self.request.GET.get('sea', 1)),
                   'internal': int(self.request.GET.get('int', 1)),
                   'direct': int(self.request.GET.get('dir', 1))}
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
        self.request.charset = 'utf8'
        cur = self.request.GET.get('cur', None)
        ref = self.request.GET.get('ref', None)
        title = self.request.GET.get('title', None)
        
        if cur is not None:
            cur = cur.encode('utf8')
        if ref is not None:
            ref = ref.encode('utf8')
        if title is not None:
            title = title.encode('utf8')
        
        if not cur:
            cur = self.request.headers.get('referer', None)

        response = Response()
        response.headers['Content-Type'] = "image/gif"
        response.headers['Expires'] = "Sat, 26 Jul 1997 05:00:00 GMT"
        response.headers['Cache-Control'] = "no-cache, must-revalidate"
        response.body = self._image

        if cur:
            hit = Hit(self._conf, cur, referrer=ref, title=title)
            self._storage.add_hit(hit)
	    return response

    def _load_component(self, filepath):
        with open('components/' + filepath) as f:
            data = f.read()
        return data

    def get_component(self):
        filepath = self.request.GET.get('file', None)
        mimetype = mimetypes.guess_type(filepath, False)
        response = Response()
        response.headers['Content-Type'] = mimetype[0]
        response.body = self._load_component(filepath)
        return response 

    def http404(self):
        response = Response()
        response.status = 404
        response.body = 'Not Found.'
        return response

    def __call__(self, environ, start_response):
        self.request = Request(environ)
        urlmap = self._conf['urlmap']
        name = self.request.path_info_pop()
        if name == '':
            name = 'index'
        method_name = urlmap.get(name, 'http404')
        method = getattr(self, method_name, None)
        response = method()
        return response(environ, start_response)


def app_factory(global_config, storage_name, **local_conf):
    config = {}
    for key, value in local_conf.iteritems():
        if key.startswith('cfg>>'):
            cfgs = key.split('>>',1)[1]
            keys = cfgs.split('>>')
            if len(keys) == 1:
                config[keys[0]] = value
            else:
                if not keys[0] in config:
                    config[keys[0]] = {}
                if len(keys) == 2:
                    config[keys[0]][keys[1]] = value
                else:
                    if not keys[1] in config[keys[0]]:
                        config[keys[0]][keys[1]] = {}
                    config[keys[0]][keys[1]][keys[2]] = value
    if storage_name == 'memory':
        storage = MemoryStorage(config)
    elif storage_name == 'sql':
        storage = SQLStorage(config)
    else:
        raise ValueError('No such storage: %s' % storage_name)
    return PopiWSGIServer(config, storage)
