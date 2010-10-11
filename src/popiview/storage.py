import operator
from popiview.counter import Counter

class MemoryStorage(object):    

    def __init__(self):
        self._hits = []
        self._recenthits = []


    def clear_hits(self):
        self._hits = []


    def add_hit(self, hit):
        hitobj = {'url': hit.url(), 'timestamp': hit.timestamp(), 
                'keywords': hit.keywords(), 'path': hit.path()}
        self._hits.append(hitobj)
        self._recenthits.append(hitobj)
    
    
    def get_recenthits(self):
        recenthits = self._recenthits[:20]
        self._recenthits = []
        
        return recenthits


    def list_urls(self, unique=False, start_time=None, end_time=None, 
                  minimum_hits=1):
        """Returns a list of all the urls. Optional parameters:
        unique Return only unique urls.
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        hits = self._hits
        
        hits = filter(self.filter_timestamp(start_time, end_time), hits)

        urls = map(operator.itemgetter('url'), hits)
 
        if unique:
            return list(set(urls))

        return urls

     
    def get_hitcount(self, url, start_time=None, end_time=None):
        """Returns number of hits for a specific url. Optional parameters:  
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        """
        hits = self._hits
        
        hits = filter(self.filter_url(url), hits)
        hits = filter(self.filter_timestamp(start_time, end_time), hits)

        return len(hits)


    def get_hitcounts(self, start_time=None, end_time=None, minimum_hits=1,
                      return_paths=True):
        """Return dictionary of hitcounts for all urls using the format 
        {url: count} Optional parameters:
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        hits = self._hits
        
        hits = filter(self.filter_timestamp(start_time, end_time), hits)

        # Get a dictionary like {url: count} or {path: count}
        if return_paths:
            hitcounts = Counter(map(operator.itemgetter('path'), hits))
        else:
            hitcounts = Counter(map(operator.itemgetter('url'), hits))
        
        # Iterate over the hitcounts, putting them through the filter function.
        # Items are removed if the filter function returns false.
        hitcounts = dict(filter(self.filter_hitcount(minimum_hits), 
                                hitcounts.iteritems()))

        return hitcounts

    
    def get_keywords(self, url=None, start_time=None, end_time=None, 
                     minimum_count=None):
        """Get all keywords and their counts.
        Returns dictionary: {keyword: count}
        """
        hits = self._hits
        
        hits = filter(self.filter_url(url), hits)
        hits = filter(self.filter_timestamp(start_time, end_time), hits)
        
        # Iterate over keywords in hits, combining them in a single list.
        # Then use Counter to get a dictionary like {keyword: count}
        keywords = Counter(reduce(operator.add,
                                  map(operator.itemgetter('keywords'), hits),
                                  []))
        
        keywords = dict(filter(self.filter_keywordcount(minimum_count), 
                        keywords.iteritems()))

        return keywords


    def filter_url(self, url=None):
        """Returns a filter function to filter hits by url.
        """
        
        def filter_function(item):
            """Filter hits by url. Return false if item doesn't match the given
            url, true otherwise.
            """
            if url is not None:
                if item['url'] != url:
                    return False
            return True

        return filter_function


    def filter_timestamp(self, start_time=None, end_time=None):
        """Return a filter function for filtering by start and end time.
        """

        def filter_function(item):
            """Filter hits by start and end time.
            Returns false if out of bounds, true otherwise.
            """
            if start_time is not None:
                if item['timestamp'] < start_time:
                    return False
            if end_time is not None:
                if item['timestamp'] > end_time:
                    return False
            return True

        return filter_function


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


    def filter_keywordcount(self, minimum_count=None):
        """Returns a filter function for filtering by minimum keyword count.
        """

        def filter_function((keyword, count),):
            """Filter keywords by minimum count.
            Returns false if count is less than minimum_count, true otherwise.
            """
            if minimum_count is not None:
                if count < minimum_count:
                    return False
            return True

        return filter_function
