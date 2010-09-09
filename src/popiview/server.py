from webob import Request, Response

class PopiWSGIServer(object):
    def __init__(self, msg):
        self.message = msg

    def GET_hello(self):
        return Response(self.message)

    def __call__(self, environ, start_response):
        self.request = Request(environ)
        method_name = '%s_%s' % (self.request.method,
                                 self.request.path_info_pop())
        method = getattr(self, method_name, None)
        if method is None:
            response = Response('Not Found')
            response.status = 404
        else:
            response = method()
        return response(environ, start_response)
        
def app_factory(global_config, msg, **local_conf):
    return PopiWSGIServer(msg)
    
