import urlparse

class Hit(object):

    def __init__(self, url, remove_www=False, referrer='', user_agent=None):

        self._url_parts = list(urlparse.urlsplit(url))
        self._remove_www = remove_www
        self._referrer_parts = list(urlparse.urlsplit(referrer))


    def url(self):
	url = self._url_parts

	if url[2].endswith('/'):
            url[2] = url[2][:-1]

        if(self._remove_www == True):
            url[1] = url[1].replace('www.', '', 1)

        return urlparse.urlunsplit(url)


    def keywords(self):
        ref = self._referrer_parts
        qs = urlparse.parse_qs(ref[3])
        keywords = qs['q'][0].decode('utf8').split(' ')
        return keywords


