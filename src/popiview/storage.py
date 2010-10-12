import operator
import MySQLdb
from popiview.counter import Counter
from popiview.filters import StorageFilters

class MemoryStorage(object):
    
    def __init__(self):
        self._hits = []
        self._recenthits = []
        self._sf = StorageFilters()


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
        
        hits = filter(self._sf.filter_timestamp(start_time, end_time), 
                      hits)

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
        
        hits = filter(self._sf.filter_url(url), hits)
        hits = filter(self._sf.filter_timestamp(start_time, end_time), 
                      hits)

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
        
        hits = filter(self._sf.filter_timestamp(start_time, end_time), 
                      hits)

        # Get a dictionary like {url: count} or {path: count}
        if return_paths:
            hitcounts = Counter(map(operator.itemgetter('path'), hits))
        else:
            hitcounts = Counter(map(operator.itemgetter('url'), hits))
        
        # Iterate over the hitcounts, putting them through the filter function.
        # Items are removed if the filter function returns false.
        hitcounts = dict(filter(self._sf.filter_hitcount(minimum_hits), 
                                hitcounts.iteritems()))

        return hitcounts

    
    def get_keywords(self, url=None, start_time=None, end_time=None, 
                     minimum_count=None):
        """Get all keywords and their counts.
        Returns dictionary: {keyword: count}
        """
        hits = self._hits
        
        hits = filter(self._sf.filter_url(url), hits)
        hits = filter(self._sf.filter_timestamp(start_time, end_time), 
                      hits)
        
        # Iterate over keywords in hits, combining them in a single list.
        # Then use Counter to get a dictionary like {keyword: count}
        keywords = Counter(reduce(operator.add,
                                  map(operator.itemgetter('keywords'), hits),
                                  []))
        
        keywords = dict(filter(self._sf.filter_keywordcount(minimum_count),
                        keywords.iteritems()))

        return keywords



class SQLStorage(object):
    
    def __init__(self):
        self._sf = StorageFilters()
        try:
            self.conn = MySQLdb.connect(host='localhost', 
                                        user='root', 
                                        passwd='qqrs',
                                        db='popiview')
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)

        self.cursor = conn.cursor()


    def __del__(self):
        self.cursor.close()
        self.conn.close()


    def clear_hits(self):
        pass


    def add_hit(self, hit):
        timestamp = hit.timestamp()
        url = hit.url()
        path = hit.path()
        referrer = hit.referrer()
        self.cursor.execute("""INSERT INTO hits (hit_timestamp, 
                                               hit_url,
                                               hit_path,
                                               hit_referrer)
                                               VALUES (%d, `%s`, `%s`, `%s`)"""
                            % (timestamp, url, path, referrer))
        

    def get_recenthits(self):
        pass


    def list_urls(self, unique=False, start_time=None, end_time=None,
                  minimum_hits=1):
        """Returns a list of all the urls. Optional parameters:
        unique Return only unique urls.
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        pass


    def get_hitcount(self, url, start_time=None, end_time=None):
        """Returns number of hits for a specific url. Optional parameters:  
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        """
        pass


    def get_hitcounts(self, start_time=None, end_time=None, minimum_hits=1,
                      return_paths=True):
        """Return dictionary of hitcounts for all urls using the format 
        {url: count} Optional parameters:
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        pass


    def get_keywords(self, url=None, start_time=None, end_time=None,
                     minimum_count=None):
        """Get all keywords and their counts.
        Returns dictionary: {keyword: count}
        """
        pass
