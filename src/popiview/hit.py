import urlparse
import time

class Hit(object):

    def __init__(self, url, referrer=None, timestamp=None):

        self._url_parts = self._urlparser(list(urlparse.urlsplit(url)))
    
        if referrer is None:
            self._referrer_parts = None
        else:
            self._referrer_parts = self._urlparser(
                list(urlparse.urlsplit(referrer)))

        if timestamp is None:
            self._timestamp = time.time()
        else:
            self._timestamp = timestamp

    def url(self):
        return urlparse.urlunsplit(self._url_parts)

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

    def _urlparser(self, url):
        # Filters is a list of dictionaries
        filters = [
            {'type': 'endswith', 'urlpart': 2, 'find': '/', 'replace': ''},
            {'type': 'replace', 'urlpart': 1, 'find': 'www.', 'replace': '',
                'limit': 1},
            {'type': 'cutoff', 'urlpart': 3, 'find': 'PHPSESSID'}]

        for f in filters:
            if f['type'] == 'endswith':
                if url[f['urlpart']].endswith(f['find']):
                    url[f['urlpart']] = url[f['urlpart']][:-len(f['find'])] + \
                        f['replace']
            elif f['type'] == 'replace':
                if f['limit']:
                    url[f['urlpart']] = url[f['urlpart']].replace(f['find'], 
                        f['replace'], f['limit'])
                else:
                    url[f['urlpart']] = url[f['urlpart']].replace(f['find'],
                        f['replace'])
            elif f['type'] == 'cutoff':
                strpos = url[f['urlpart']].find(f['find'])
                print str(strpos) + ' -----------------------'
                if strpos >= 0:
                    url[f['urlpart']] = url[f['urlpart']][:-strpos]
        return url
