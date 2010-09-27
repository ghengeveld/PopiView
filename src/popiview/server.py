from webob import Request, Response
from popiview.hit import Hit
from popiview.storage import MemoryStorage

class PopiWSGIServer(object):
    def __init__(self, storage):
        self.storage = storage

    def index(self):
        return Response('<html></head><title>Test</title></head><body>test</body></html>')

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
	method_name = {'image.gif': 'image_gif'}.get(name, name)
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
    else:
        raise ValueError('No such storage: %s' % storage_name)
    return PopiWSGIServer(storage)
