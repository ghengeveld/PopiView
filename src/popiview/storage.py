import operator
from popiview.counter import Counter

class MemoryStorage(object):
    

    def __init__(self):
        self._hits = []


    def clear_hits(self):
        self._hits = []


    def add_hit(self, hit):
        self._hits.append({'url': hit.url(), 'timestamp': hit.timestamp(), 
                           'keywords': hit.keywords()})


    def list_urls(self, unique=False, start_time=None, end_time=None, 
                  minimum_hits=1):
        """Returns a list of all the urls. Optional parameters:
        unique Return only unique urls.
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        hits = self._hits
        
        selection = self.filter_timestamp(hits, start_time, end_time)

        urls = []
        for item in selection:
            urls.append(item['url'])
        
        if unique:
            return list(set(urls))

        return urls

     
    def get_hitcount(self, url, start_time=None, end_time=None):
        """Returns number of hits for a specific url. Optional parameters:  
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        """
        hits = self._hits
        
        hits = self.filter_url(hits, url)
        hits = self.filter_timestamp(hits, start_time, end_time)

        return len(hits)


    def get_hitcounts(self, start_time=None, end_time=None, minimum_hits=1):
        """Return dictionary of hitcounts for all urls using the format 
        {url: count} Optional parameters:
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        hits = self._hits
        
        hits = self.filter_timestamp(hits, start_time, end_time)

        # Get a dictionary like {url: count}
        hitcount = Counter(map(operator.itemgetter('url'), hits))
        
        # Iterate over the hitcounts, putting them through the filter function.
        # Items are removed if the filter function returns false.
        return dict(filter(self.filter_hitcount(minimum_hits), 
                           hitcount.iteritems()))

    
    def get_keywords(self, url=None, start_time=None, end_time=None):
        """Get all keywords. Returns dictionary: {keyword: count}
        """
        hits = self._hits
        
        if url is not None:
            hits = self.filter_url(hits, url)
        
        hits = self.filter_timestamp(hits, start_time, end_time)
        
        # Iterate over keywords in hits, combining them in a single list.
        # Then use Counter to get a dictionary like {keyword: count}
        keywords = Counter(reduce(operator.add,
                                  map(operator.itemgetter('keywords'), hits)))

        return keywords


    def filter_url(self, hits, url):
        """Filter hits by url. Return only hits for the given url.
        """
        selection = []

        for item in hits:
            if item['url'] == url:
                selection.append(item)
        
        return selection


    def filter_timestamp(self, hits, start_time=None, end_time=None):
        """Filter hits by start and end time. Return only hits between these
        timestamps.
        """
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


    def filter_hitcount(self, minimum_hits=None, maximum_hits=None):
        """Returns a filter function for filtering by minimum and maximum hits.
        """
        def filter_function((url, count),):
            """Filter hitcounts by minimum or maximum number of hits.
            Returns false if out of bounds, true otherwise.
            """
            if minimum_hits is not None:
                if count < minimum_hits:
                    return False
            if maximum_hits is not None:
                if count > maximum_hits:
                    return False
            return True

        return filter_function
