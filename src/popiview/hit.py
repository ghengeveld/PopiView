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
        if self._url_parts[3]:
            return self._url_parts[2] + '?' + self._url_parts[3]
        return self._url_parts[2] 

    def timestamp(self):
        return self._timestamp

    def referrer(self):
        if self._referrer_parts is None:
            return None
        return urlparse.urlunsplit(self._referrer_parts)

    def searchquery(self):
        ref = self._referrer_parts
        sites = [('Google', '.google.', 'q'), 
                 ('Yahoo', '.yahoo.', 'p'),
                 ('Bing', '.bing.', 'q')]
    
        for site in sites:
            if ref[1].find(site[1]) > -1:
                qs = urlparse.parse_qs(ref[3])
                query = qs.get(site[2], [])
                if query is not []:
                    return (site[0], query[0])
        return None

    def keywords(self):
        keywords = []
        query = self.searchquery()
        if query is not None:
            keywords += query[1].lower().decode('utf8').split(' ')
        return keywords

    def source(self):
        url = self._url_parts
        ref = self._referrer_parts

        if ref is None or ref[1] == '':
            return 'direct'
        if url[1] == ref[1]:
            return 'internal'
        query = self.searchquery()
        if query is not None:
            return query[0] + ': ' + query[1]
        return 'unknown'
