import sys
import time
import operator
import MySQLdb
import threading
from popiview.counter import Counter
from popiview.filters import StorageFilters

class MemoryStorage(object):
    
    def __init__(self, config):
        self._conf = config
        self._hits = []
        self._recenthits = []
        self._sf = StorageFilters()

    def clear_hits(self):
        self._hits = []

    def add_hit(self, hit):
        hitobj = {'url': hit.url(), 'timestamp': hit.timestamp(), 
                  'keywords': hit.keywords(), 'path': hit.path(), 
                  'title': hit.title(), 'source': hit.source()}
        if not self._sf.filter_path(hit.path()):
            # Don't store hits for blacklisted paths
            return
        self._hits.append(hitobj)
        self._recenthits.append(hitobj)
        if len(self._recenthits) > 20:
            self._recenthits = self._recenthits[-20:]
    
    def get_recenthits(self, sources, last_timestamp=0):
        recenthits = self._recenthits
        recenthits = filter(self._sf.filter_timestamp(
                                start_time = last_timestamp),
                            recenthits)
        recenthits = filter(self._sf.filter_sources(sources), recenthits)
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
                      qfield='hit_path'):
        """Return dictionary of hitcounts for all urls using the format 
        {name: count} Optional parameters:
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        hits = self._hits
        
        hits = filter(self._sf.filter_timestamp(start_time, end_time), 
                      hits)

        # Get a dictionary like {url: count} or {path: count}
        if qfield == 'hit_url':
            hitcounts = Counter(map(operator.itemgetter('url'), hits))
        elif qfield == 'hit_title':
            hitcounts = Counter(map(operator.itemgetter('title'), hits))
        else:
            hitcounts = Counter(map(operator.itemgetter('path'), hits))
        
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


class StorageError(StandardError):
    print '---------------- Storage Error ----------------'  


class SQLStorage(object):
    
    def __init__(self, config):
        self._conf = config
        self.localdata = threading.local()
        self.lastrecenthitsrequest = 0
        self._recenthits = []
        self._sf = StorageFilters()

    def get_connection(self):
        if not hasattr(self.localdata, 'db'):
            self.localdata.db = self._create_connection()
        return self.localdata.db

    def _create_connection(self):
        cfg = self._conf
        try:
            return MySQLdb.connect(host = cfg['dbhost'], 
                                   user = cfg['dbuser'], 
                                   passwd = cfg['dbpass'],
                                   db = cfg['dbname'])
        except MySQLdb.Error, e:
            raise StorageError(str(e))

    def _close_connection(self):
        if hasattr(self.localdata, 'db'):
            self.localdata.db.close()

    def __del__(self):
        self._close_connection()

    def clear_hits(self):
        conn = self.get_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("TRUNCATE TABLE hits_keywords")
        cursor.execute("TRUNCATE TABLE hits")
        cursor.close()

    def add_hit(self, hit):
        conn = self.get_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        timestamp = int(hit.timestamp())
        url = hit.url()
        path = hit.path()
        title = hit.title()
        referrer = hit.referrer()
        keywords = hit.keywords()
        source = hit.source()
        if not self._sf.filter_path(path):
            # Don't store hits for blacklisted paths
            return
        cursor.execute("INSERT INTO hits (hit_timestamp, hit_url,\
                                          hit_path, hit_title, hit_referrer)\
                        VALUES ('%(timestamp)i', '%(url)s',\
                                '%(path)s', '%(title)s', '%(referrer)s')" % {
                       'timestamp': timestamp, 'url': url, 
                       'path': path, 'title': title, 'referrer': referrer})
        hitid = cursor.lastrowid
        for word in keywords:
            cursor.execute("INSERT INTO hits_keywords (hit_id, keyword)\
                            VALUES ('%(hitid)i', '%(keyword)s')" % {
                           'hitid': hitid, 'keyword': word})
        cursor.close()
        hitobj = {'url': url, 'timestamp': timestamp, 'title': title, 
                  'keywords': keywords, 'path': path, 'source': source}
        self._recenthits.append(hitobj)
        if len(self._recenthits) > 20:
            self._recenthits = self._recenthits[-20:]
        
    def get_recenthits(self, sources, last_timestamp=0):
        recenthits = self._recenthits
        recenthits = filter(self._sf.filter_timestamp(
                                start_time = last_timestamp),
                            recenthits)
        recenthits = filter(self._sf.filter_sources(sources), recenthits)
        return recenthits
    
    def __get_recenthits(self):
        conn = self.get_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT hit_timestamp AS timestamp,\
                               hit_url AS url,\
                               hit_path AS path,\
                               hit_title AS title\
                        FROM hits WHERE hit_timestamp > %i \
                        ORDER BY hit_timestamp DESC LIMIT 20" % (
                       self.lastrecenthitsrequest))
        recenthits = list(cursor.fetchall())
        cursor.close()
        if recenthits:
            self.lastrecenthitsrequest = recenthits[0]['timestamp']
        return recenthits

    def list_urls(self, unique=False, start_time=None, end_time=None,
                  minimum_hits=1):
        """Returns a list of all the urls. Optional parameters:
        unique Return only unique urls.
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        conn = self.get_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT hit_url FROM hits")
        urls = cursor.fetchall().values()
        cursor.close()

        urls = filter(self._sf.filter_timestamp(start_time, end_time), 
                      urls)

        if unique:
            return list(set(urls))
        
        return urls

    def get_hitcount(self, url, start_time=None, end_time=None):
        """Returns number of hits for a specific url. Optional parameters:  
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        """
        conn = self.get_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        qstart = ''
        qend = ''
        if start_time is not None:
            qstart = " AND hit_timestamp >= %i" % (start_time)
        if end_time is not None:
            qend = " AND hit_timestamp <= %i" % (end_time)

        cursor.execute("SELECT COUNT(hit_url) AS count FROM hits \
                        WHERE hit_url = '%s'%s%s" % (url, qstart, qend))
        count = cursor.fetchone()['count']
        cursor.close()
        return count

    def get_hitcounts(self, start_time=None, end_time=None, minimum_hits=1,
                      qfield='hit_path'):
        """Return dictionary of hitcounts for all urls using the format 
        {url: count}. Optional parameters:
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        conn = self.get_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        qstart = ''
        qend = ''
        if qfield not in ['hit_url', 'hit_path', 'hit_title']:
            qfield = 'hit_path'
        if start_time is not None:
            qstart = " AND hit_timestamp >= %i" % (start_time)
            pass
        if end_time is not None:
            qend = " AND hit_timestamp <= %i" % (end_time)
            pass

        cursor.execute("SELECT %s AS name, COUNT(hit_url) AS count \
                        FROM hits WHERE 1=1%s%s GROUP BY hit_url" % (
                       qfield, qstart, qend))
        counts = {}
        res = list(cursor.fetchall())
        cursor.close()
        for item in res:
            counts[item['name']] = item['count']
        return counts

    def get_keywords(self, url=None, start_time=None, end_time=None,
                     minimum_count=None):
        """Get all keywords and their counts.
        Returns dictionary: {keyword: count}
        """
        conn = self.get_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT keyword, COUNT(keyword) AS count \
                        FROM hits_keywords GROUP BY keyword")
        keywords = {}
        res = list(cursor.fetchall())
        cursor.close()
        for item in res:
            keywords[item['keyword']] = item['count']
        return keywords
