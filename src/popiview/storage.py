class MemoryStorage(object):
    

    def __init__(self):
        self._hits = []


    def clear_hits(self):
        self._hits = []


    def add_hit(self, hit):
        self._hits.append({'url': hit.url(), 'timestamp': hit.timestamp(), 'keywords': hit.keywords()})


    def list_urls(self, unique=False, start_time=None, end_time=None, minimum_hits=1):
        hits = self._hits
        
        selection = self.filter_timestamp(hits, start_time, end_time)

        urls = []
        for item in selection:
            urls.append(item['url'])
        
        if unique:
            return list(set(urls))

        return urls


    def get_hitcount(self, url, start_time=None, end_time=None, minimum_hits=1):
        hits = self._hits
        
        hits = self.filter_url(hits, url)
        hits = self.filter_timestamp(hits, start_time, end_time)

        return len(hits)


    def get_hitcounts(self, start_time=None, end_time=None, minimum_hits=1):
        hits = self._hits
        hitcounts = {}

        hits = self.filter_timestamp(hits, start_time, end_time)

        for item in hits:
            if hitcounts.has_key(item['url']):
                hitcounts[item['url']] += 1
            else:
                hitcounts[item['url']] = 1

        return hitcounts

    def get_keywords(self, url, start_time=None, end_time=None):
        hits = self._hits
        keywords = {}
        
        hits = self.filter_url(hits, url)
        hits = self.filter_timestamp(hits, start_time, end_time)
        
        for item in hits:
            for keyword in item['keywords']:
                if keywords.has_key(keyword):
                    keywords[keyword] += 1
                else:
                    keywords[keyword] = 1

        return keywords


    def filter_url(self, hits, url):
        selection = []

        for item in hits:
            if item['url'] == url:
                selection.append(item)
        
        return selection


    def filter_timestamp(self, hits, start_time=None, end_time=None):
        if start_time is None and end_time is None:
            return hits

        selection = []
        if start_time is None:
            for item in hits:
                if item['timestamp'] <= end_time:
                    selection.append(item)
        elif end_time is None:
            for item in hits:
                if item['timestamp'] >= start_time:
                    selection.append(item)
        else:
            for item in hits:
                if (item['timestamp'] <= end_time 
                        and item['timestamp'] >= start_time):
                    selection.append(item)

        return selection
