import urlparse
import time
from popiview.urlparser import URLParser

class Hit(object):

    def __init__(self, config, url, referrer=None, title=None, 
            timestamp=None, visitor_ip=None):
        self._conf = config
        self._urlp = URLParser(config)

        if url.endswith('/'):
            url = url[:-1]
        self._url_parts = urlparse.urlsplit(url)
    
        if referrer is None:
            self._referrer_parts = None
        else:
            self._referrer_parts = urlparse.urlsplit(referrer)
        
        if title is None:
            self._title = ''
        elif config['title_strip']:
            self._title = title.replace(config['title_strip'], '').strip()
        else:
            self._title = title.strip()

        if timestamp is None:
            self._timestamp = int(time.time())
        else:
            self._timestamp = int(timestamp)
        
        if visitor_ip is None:
            self._visitor_ip = ''
        else:
            self._visitor_ip = visitor_ip

    def url(self):
        if self._url_parts is None:
            return None
        return self._url_parts.geturl()

    def path(self):
        if self._url_parts[3]:
            return self._url_parts[2] + '?' + self._url_parts[3]
        return self._url_parts[2] 

    def referrer(self):
        if self._referrer_parts is None:
            return None
        return self._referrer_parts.geturl()

    def title(self):
        return self._title

    def timestamp(self):
        return self._timestamp

    def keywords(self):
        return self._urlp.keywords(self._referrer_parts)

    def source(self):
        return self._urlp.source(self._url_parts, self._referrer_parts)

    def is_whitelisted(self):
        if 'whitelist_lvl1' in self._conf:
            if self._conf['whitelist_lvl1'] == '':
                return True
            whitelist_items = [x.strip() for x in list(
                self._conf['whitelist_lvl1'].split(','))]
            pathlevels = self.path().strip('/').split('/')
            if pathlevels:
                lvl1 = pathlevels[0]
            if lvl1 in whitelist_items:
                return True
            return False
        return True

    def is_blacklisted(self):
        if 'ip_blacklist' in self._conf:
            blacklist_items = self._conf['ip_blacklist'].split(',')
            if self._visitor_ip in blacklist_items:
                return True
        return False
