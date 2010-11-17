import urlparse
import re
from popiview.utils import get_unicode

class URLParser(object):

    def __init__(self, config):
        self._conf = config

    def searchquery(self, ref):
        sites = self._conf['sparams']
        if ref is not None:
            for domain, q in sites.iteritems():
                domainpos = ref[1].find(domain)
                if domainpos > -1:
                    qs = urlparse.parse_qs(ref[3])
                    query = qs.get(q, None)
                    if query and query[0] and ref[1][domainpos:]:
                        return (ref[1][domainpos:], get_unicode(query[0]))
        return None

    def keywords(self, ref):
        keywords = []
        query = self.searchquery(ref)
        if query is not None:
            phrase = query[1].lower()
            pattern = re.compile(r'".*?"|\'.*\'|[^\s]+')
            for match in re.finditer(pattern, phrase):
                item = match.group(0)
                if item.startswith('"') or item.startswith("'"):
                    item = item[1:-1]
                keywords.append(item)
        return keywords

    def source(self, url, ref):
        if ref is None or ref[1] == '':
            return 'direct'
        if url[1] == ref[1]:
            return 'internal'
        query = self.searchquery(ref)
        if query is not None:
            return 'searches - ' + query[0] + ': ' + get_unicode(query[1])
        return 'external: ' + ref[1]

    def urlfilter(self, url):
        # Filters is a list of dictionaries
        filters = [
            {'type': 'endswith', 'urlpart': 2, 'find': '/', 'replace': ''},
            {'type': 'endswith', 'urlpart': 2, 'find': '/homepage', 
                'replace': ''},
            {'type': 'endswith', 'urlpart': 2, 'find': '/cultuur', 
                'replace': ''},
            {'type': 'endswith', 'urlpart': 2, 'find': '/eten-drinken', 
                'replace': ''},
            {'type': 'endswith', 'urlpart': 2, 'find': '/opinie', 
                'replace': ''},
            #{'type': 'replace', 'urlpart': 1, 'find': 'www.', 'replace': '',
            #    'limit': 1},
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
                if strpos >= 0:
                    print url[f['urlpart']] + ' (' + str(strpos) + ')'
                    url[f['urlpart']] = url[f['urlpart']][:strpos]
            if url[3].endswith('&'):
                url[3] = url[3][:-1]
        return url
