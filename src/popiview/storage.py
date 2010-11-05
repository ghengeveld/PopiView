import operator
import MySQLdb
import MySQLdb.cursors
import sqlite3
import threading
import urlparse
from popiview.counter import Counter
from popiview.filters import StorageFilters
from popiview.urlparser import URLParser
from popiview.htmlparser import HTMLParser


class MemoryStorage(object):

    def __init__(self, config):
        self._conf = config
        self._hits = []
        self._recenthits = []
        self._sf = StorageFilters()

    def clear_hits(self):
        self._hits = []
        self._recenthits = []

    def add_hit(self, hit):
        hitobj = {'url': hit.url(), 'timestamp': hit.timestamp(),
                  'keywords': hit.keywords(), 'path': hit.path(),
                  'title': hit.title(), 'source': hit.source()}
        if not self._sf.filter_path(hit.path()):
            # Don't store hits for blacklisted paths
            return
        self._hits.append(hitobj)
        self._recenthits.append(hitobj)
        recenthits_size = int(self._conf['recenthits_size'])
        if len(self._recenthits) > recenthits_size:
            self._recenthits = self._recenthits[-recenthits_size:]

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

    def list_searches(self, keyword=None):
        """List all the search phrases which contain the given keyword, or all
        phrases if no keyword given.
        """
        phrases = []
        sources = map(operator.itemgetter('source'), self._hits)
        sources = {}.fromkeys(sources).keys() # make unique
        htmlparser = HTMLParser()
        for source in sources:
            if source.startswith('searches'):
                qpos = source.find(': ')
                if qpos > 0:
                    phrase = source[qpos+2:]
                    if keyword is None or phrase.find(keyword) != -1:
                        phrases.append(htmlparser.escape(phrase))
        return phrases


class StorageError(StandardError):

    def __init__(self, value):
        self.message = value
        print '-'*10 + value

    def __str__(self):
        return repr(self.message)


class SQLStorage(object):

    def __init__(self, config):
        self._conf = config
        self.localdata = threading.local()
        self.lastrecenthitsrequest = 0
        self._recenthits = []
        self._sf = StorageFilters()
        self._setup()

    def __del__(self):
        self._close_connection()

    def get_connection(self):
        if not hasattr(self.localdata, 'db'):
            self.localdata.db = self._create_connection()
            if self._conf['dbtype'] == 'mysql':
                self.localdata.db.set_character_set('utf8')
                if hasattr(self.localdata.db, 'autocommit'):
                    self.localdata.db.autocommit(1)
        return self.localdata.db

    def get_cursor(self, DictCursor=True):
        conn = self.get_connection()
        if self._conf['dbtype'] == 'mysql' and DictCursor==True:
            return conn.cursor(MySQLdb.cursors.DictCursor)
        else:
            return conn.cursor()

    def _create_connection(self):
        cfg = self._conf
        if cfg['dbtype'] == 'mysql':
            try:
                return MySQLdb.connect(host = cfg['dbhost'],
                                       user = cfg['dbuser'],
                                       passwd = cfg['dbpass'],
                                       db = cfg['dbname'])
            except MySQLdb.Error, e:
                raise StorageError(str(e))
        else:
            try:
                return sqlite3.connect(cfg['dbfile'])
            except sqlite3.Error, e:
                raise StorageError(str(e))        

    def _close_connection(self):
        if hasattr(self.localdata, 'db'):
            self.localdata.db.close()

    def _setup(self):
        cursor = self.get_cursor()
        #cursor.execute("DROP TABLE IF EXISTS hits")
        #cursor.execute("DROP TABLE IF EXISTS hits_keywords")
        if self._conf['dbtype'] == 'mysql':
            # MySQL syntax
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS hits (
              hit_id int(32) NOT NULL AUTO_INCREMENT,
              hit_timestamp int(32) NOT NULL,
              hit_url varchar(500) COLLATE utf8_unicode_ci NOT NULL,
              hit_path varchar(500) COLLATE utf8_unicode_ci NOT NULL,
              hit_title varchar(200) COLLATE utf8_unicode_ci NOT NULL,
              hit_referrer varchar(1000) COLLATE utf8_unicode_ci NOT NULL,
              PRIMARY KEY (hit_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci
            AUTO_INCREMENT=1""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS hits_keywords (
              hit_id int(32) NOT NULL,
              keyword varchar(100) COLLATE utf8_unicode_ci NOT NULL,
              PRIMARY KEY (hit_id, keyword)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci""")
        else:
            # SQLite syntax
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS hits (
              hit_id INTEGER,
              hit_timestamp INTEGER,
              hit_url varchar(500),
              hit_path varchar(500),
              hit_title varchar(200),
              hit_referrer varchar(1000),
              PRIMARY KEY (hit_id)
            )""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS hits_keywords (
              hit_id INTEGER,
              keyword varchar(100),
              PRIMARY KEY (hit_id, keyword),
              FOREIGN KEY (hit_id) REFERENCES hits(hit_id)
            )""")
        cursor.close()

    def clear_hits(self):
        self._recenthits = []
        cursor = self.get_cursor()
        if self._conf['dbtype'] == 'mysql':
            # MySQL syntax
            cursor.execute("TRUNCATE TABLE hits_keywords")
            cursor.execute("TRUNCATE TABLE hits")
        else:
            # SQLite syntax
            cursor.execute("DELETE FROM hits_keywords")
            cursor.execute("DELETE FROM hits")
        cursor.close()

    def add_hit(self, hit):
        cursor = self.get_cursor()
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
        cursor.execute("""INSERT INTO hits (`hit_timestamp`, `hit_url`,
                            `hit_path`, `hit_title`, `hit_referrer`)
                          VALUES ('%(timestamp)i', '%(url)s',
                                '%(path)s', '%(title)s', '%(referrer)s')""" % {
                       'timestamp': timestamp, 'url': url,
                       'path': path, 'title': title, 'referrer': referrer})
        hitid = cursor.lastrowid
        for word in keywords:
            if self._conf['dbtype'] == 'sqlite':
                cursor.execute("""INSERT OR IGNORE INTO hits_keywords ( 
                                  `hit_id`, `keyword`
                                  ) VALUES ('%(hitid)i', '%(keyword)s');""" % {
                                  'hitid': hitid, 'keyword': word})
            else:
                cursor.execute("""INSERT IGNORE INTO hits_keywords (
                                  `hit_id`, `keyword`
                                  ) VALUES ('%(hitid)i', '%(keyword)s');""" % {
                                  'hitid': hitid, 'keyword': word})
        #conn.commit()
        cursor.close()
        hitobj = {'url': url, 'timestamp': timestamp, 'title': title,
                  'keywords': keywords, 'path': path, 'source': source}
        self._recenthits.append(hitobj)
        recenthits_size = int(self._conf['recenthits_size'])
        if len(self._recenthits) > recenthits_size:
            self._recenthits = self._recenthits[-recenthits_size:]

    def get_recenthits(self, sources, last_timestamp=0):
        recenthits = self._recenthits
        recenthits = filter(self._sf.filter_sources(sources), recenthits)
        recenthits = filter(self._sf.filter_timestamp(
                                start_time = last_timestamp), recenthits)
        return recenthits

    def __get_recenthits(self):
        cursor = self.get_cursor()
        cursor.execute("""SELECT hit_timestamp AS timestamp,
                                 hit_url AS url,
                                 hit_path AS path,
                                 hit_title AS title
                          FROM hits WHERE hit_timestamp > %i
                          ORDER BY hit_timestamp DESC LIMIT 20""" % (
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
        cursor = self.get_cursor()
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
        cursor = self.get_cursor()
        qstart = ''
        qend = ''
        if start_time is not None:
            qstart = " AND hit_timestamp >= %i" % (start_time)
        if end_time is not None:
            qend = " AND hit_timestamp <= %i" % (end_time)

        cursor.execute("""SELECT COUNT(hit_url) AS count FROM hits
                          WHERE hit_url = '%s'%s%s""" % (url, qstart, qend))
        if isinstance(cursor, MySQLdb.cursors.DictCursor):
            count = cursor.fetchone()['count']
        else:
            count = cursor.fetchone()[0]
        cursor.close()
        return count

    def get_hitcounts(self, start_time=None, end_time=None, minimum_hits=1,
                      qfield='hit_path'):
        """Return dictionary of hitcounts for all urls using the format
        {name: count}. Optional parameters:
        start_time Return only urls requested after this timestamp.
        end_time Return only urls requested before this timestamp.
        minimum_hits Return only urls with at least this amount of hits.
        """
        cursor = self.get_cursor()
        qstart = ''
        qend = ''
        if qfield not in ['hit_url', 'hit_path', 'hit_title']:
            qfield = 'hit_path'
        if start_time is not None:
            qstart = " AND hit_timestamp >= %i" % (start_time)
            pass
        if end_time is not None:
            qend = " AND hit_timestamp < %i" % (end_time)
            pass

        cursor.execute("""SELECT %(qfield)s AS name, COUNT(%(qfield)s) AS count
                          FROM hits WHERE 1=1%(qstart)s%(qend)s
                          GROUP BY %(qfield)s""" % { 'qfield': qfield, 
                              'qstart': qstart, 'qend': qend})
        counts = {}
        res = list(cursor.fetchall())
        cursor.close()
        for item in res:
            if isinstance(cursor, MySQLdb.cursors.DictCursor):
                counts[item['name']] = item['count']
            else:
                counts[item[0]] = item[1]
        return counts

    def get_keywords(self, url=None, start_time=None, end_time=None,
                     minimum_count=None):
        """Get all keywords and their counts.
        Returns dictionary: {keyword: count}
        """
        cursor = self.get_cursor()
        cursor.execute("""SELECT keyword, COUNT(keyword) AS count
                          FROM hits_keywords GROUP BY keyword""")
        keywords = {}
        res = list(cursor.fetchall())
        cursor.close()
        for item in res:
            if isinstance(cursor, MySQLdb.cursors.DictCursor):
                keywords[item['keyword']] = item['count']
            else:
                keywords[str(item[0])] = item[1]
        return keywords

    def list_referrers(self, url=None, urlsearch=None, refsearch=None):
        """List all referrers (to a certain url)."""
        referrers = []
        cursor = self.get_cursor(DictCursor=False)
        qand = ''
        if url is not None:
            qand += " AND hit_url = '%s'" % url
        if urlsearch is not None:
            qand += " AND hit_url LIKE '%s'" % ('%'+urlsearch+'%',)
        if refsearch is not None:
            qand += " AND hit_referrer LIKE '%s'" % ('%'+refsearch+'%',)
        cursor.execute("""SELECT hit_referrer FROM hits
                          WHERE hit_referrer != '' 
                          AND hit_referrer != 'None' %s""" % qand)
        res = cursor.fetchall()
        for ref in res:
            referrers.append(ref[0])
        return referrers

    def list_searches(self, keyword=None):
        """List all the search phrases which contain the given keyword, or all
        phrases if no keyword given.
        """
        phrases = []
        urlparser = URLParser(self._conf)
        htmlparser = HTMLParser()
        if keyword is None:
            referrers = self.list_referrers()
        else:
            referrers = self.list_referrers(refsearch=keyword)
        for ref in referrers:
            ref = list(urlparse.urlsplit(ref))
            if ref is not None:
                querydata = urlparser.searchquery(ref)
                if querydata is not None:
                    phrases.append(htmlparser.escape(querydata[1]))
        return phrases
