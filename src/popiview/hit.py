import urlparse
import time
from popiview.urlparser import URLParser

class Hit(object):

    def __init__(self, config, url, referrer=None, title=None, timestamp=None):
        self._conf = config
        self._urlp = URLParser(config)
        self._url_parts = self._urlp.urlfilter(list(urlparse.urlsplit(url)))
    
        if referrer is None:
            self._referrer_parts = None
        else:
            self._referrer_parts = self._urlp.urlfilter(
                list(urlparse.urlsplit(referrer)))
        
        if title is None:
            self._title = ''
        else:
            self._title = title

        if timestamp is None:
            self._timestamp = int(time.time())
        else:
            self._timestamp = int(timestamp)

    def url(self):
        return urlparse.urlunsplit(self._url_parts)

    def path(self):
        if self._url_parts[3]:
            return self._url_parts[2] + '?' + self._url_parts[3]
        return self._url_parts[2] 

    def referrer(self):
        if self._referrer_parts is None:
            return None
        return urlparse.urlunsplit(self._referrer_parts)

    def title(self):
        return self._title

    def timestamp(self):
        return self._timestamp

    def keywords(self):
        return self._urlp.keywords(self._referrer_parts)

    def source(self):
        return self._urlp.source(self._url_parts, self._referrer_parts)
