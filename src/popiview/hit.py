import urlparse
import time

class Hit(object):

    def __init__(self, url, remove_www=False, referrer=None, timestamp=None):

        self._url_parts = list(urlparse.urlsplit(url))
        self._remove_www = remove_www
    
        if referrer is None:
            self._referrer_parts = None
        else:
            self._referrer_parts = list(urlparse.urlsplit(referrer))

        if timestamp is None:
            self._timestamp = time.time()
        else:
            self._timestamp = timestamp


    def url(self):
        url = self._url_parts
        
        if url[2].endswith('/'):
            url[2] = url[2][:-1]

        if(self._remove_www == True):
            url[1] = url[1].replace('www.', '', 1)

        return urlparse.urlunsplit(url)


    def path(self):
        return self._url_parts[2] 


    def timestamp(self):
        return self._timestamp


    def referrer(self):
        if self._referrer_parts is None:
            return None
        return urlparse.urlunsplit(self._referrer_parts)
    

    def keywords(self):
        keywords = []
        ref = self._referrer_parts
        
        if ref is None:
            return []

        qs = urlparse.parse_qs(ref[3])
        for query_string in ['q', 'query']:
            for query in qs.get(query_string, []):
                keywords += query.lower().decode('utf8').split(' ')
        
        return keywords


