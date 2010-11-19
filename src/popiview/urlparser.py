import urlparse
import re
from urllib import unquote
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
                        return (ref[1][domainpos:], query[0])
        return None

    def keywords(self, ref):
        keywords = []
        query = self.searchquery(ref)
        if query is not None:
            phrase = query[1]
            pattern = re.compile(r'".*?"|\'.*\'|[^\s]+')
            for match in re.finditer(pattern, phrase):
                item = match.group(0)
                if item.startswith('"') or item.startswith("'"):
                    item = item[1:-1]
                keywords.append(item)
        return keywords

    def source(self, url, ref):
        if ref is None or ref[1] == '':
            return u'direct'
        if url[1] == ref[1]:
            return u'internal'
        query = self.searchquery(ref)
        if query is not None:
            return (u'searches - ' + query[0] + u': ' + query[1])
        return u'external: ' + get_unicode(ref[1])
