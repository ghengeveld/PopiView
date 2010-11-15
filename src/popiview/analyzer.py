import time
from popiview.htmlparser import HTMLParser

class Analyzer(object):

    def __init__(self, storage):
        self._storage = storage

    def get_top_deviators(self, limit=None, sort_absolute=True,
                          qfield='hit_title', start_time=None,
                          boundary_time=None, end_time=None):
        """Returns a list containing top deviators, each represented in a
        dictionary: {'name': name, 'pct': deviation_pct, 'hph': deviation_abs}
        Sorted by deviation pct, optionally absolute.
        """
        deviators = []
        
        if start_time is None:
            start_time = time.time() - (3600 * 25)
        if boundary_time is None:
            boundary_time = time.time() - 3600
        if end_time is None:
            end_time = time.time()

        historic = self._storage.get_hitcounts(start_time=start_time,
            end_time=boundary_time, qfield=qfield)
        recent = self._storage.get_hitcounts(start_time=boundary_time, 
            end_time=end_time, qfield=qfield)
        historic_length = boundary_time - start_time
        recent_length = end_time - boundary_time

        for name, recent_value in recent.iteritems():
            historic_value = historic.get(name, 0.0)
            if recent_value < 5 or historic_value < 10:
                continue
            recent_hps = recent_value / float(recent_length)
            historic_hps = historic_value / float(historic_length)
            deviation_pct = int(round(
                (recent_hps - historic_hps) / historic_hps * 100.0)) 
            deviators.append({
                'name': name, 
                'pct': deviation_pct, 
                'hph_recent': int(recent_hps * 3600),
                'hph_historic': int(historic_hps * 3600),
                'num_recent': recent_value, 
                'num_historic': historic_value
            })

        # Reverse sort by deviation pct value
        if sort_absolute:
            deviators.sort(key=lambda x: abs(x['pct']), reverse=True)
        else:
            deviators.sort(key=lambda x: x['pct'], reverse=True)

        if limit is None:
            return deviators
        return deviators[:limit]

    def get_top_pages(self, limit=None, qfield='hit_title', 
            start_time=None, end_time=None, timespan=None):
        """Returns a list of pages with highest hitcount over a recent period.
        Will use either start/end time or a timespan. In case of timespan it
        uses current time as end time and calculate start time from timespan.
        """
        pages = []

        if timespan is not None:
            start_time = int(time.time()) - int(timespan)
            end_time = int(time.time())
        else:
            if start_time is None and end_time is None:
                start_time = int(time.time()) - 3600
                end_time = int(time.time())
            elif start_time is None:
                start_time = int(end_time) - 3600
            elif end_time is None:
                end_time = int(time.time())

        hitcounts = self._storage.get_hitcounts(start_time=start_time,
                end_time=end_time, qfield=qfield)

        for name, count in hitcounts.iteritems():
            hph = round(count / float(int(end_time) - int(start_time)) * 3600.0)
            pages.append({'name': name, 'count': count, 'hph': hph})

        pages.sort(key=lambda x: x['count'], reverse=True)

        if limit is None:
            return pages
        return pages[:limit]

    def get_keyword_cloud(self, minimum_count=None, limit=50,
                          minimum_pct=0, maximum_pct=100):
        """Returns a list of tuples of keywords and their size relative to the
        others, as a percentage with set bounds. Sorted alphabetically.
        """
        cloud = []
        parser = HTMLParser()
        
        keywords = self._storage.get_keywords(minimum_count=minimum_count)

        limitval = 0
        vals = keywords.values()
        vals.sort(reverse=True)
        if limit < len(keywords):
            vals = vals[:limit]
            limitval = vals[-1]

        totalcount = sum(vals)
        pct_range = maximum_pct - minimum_pct
        keys = keywords.keys()
        keys.sort()

        for keyword in keys:
            if limitval and keywords[keyword] < limitval:
                continue
            pct = (keywords[keyword] / float(totalcount) * pct_range
                   + minimum_pct)
            keyword = parser.escape(keyword)
            cloud.append((keyword, round(pct)))
        return sorted(cloud)

    def calc_sd(self, numlist):
        """Returns the standard deviation for a list of numbers.
        """
        if len(numlist):
            avg = sum(numlist) / len(numlist)
            devs = []
            for num in numlist:
                devs.append((num - avg) ** 2)
            if len(devs):
                return (sum(devs) / len(devs)) ** 0.5
        return 0.0


    def relative_url(self, url):
        """Returns relative url
        """
        return
