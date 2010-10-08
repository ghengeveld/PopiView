import time

class Analyzer(object):

    def __init__(self, storage, start_time=None, boundary_time=None, 
                 end_time=None):
        self._storage = storage
        now = time.time()
        
        if start_time is None:
            self._start_time = now - 3600 * 24
        else:
            self._start_time = start_time
        
        if boundary_time is None:
            self._boundary_time = now - 3600
        else:
            self._boundary_time = boundary_time
        
        if end_time is None:
            self._end_time = now
        else:
            self._end_time = end_time


    def get_top_deviators(self, limit=None, sort_absolute=True):
        """Returns a list containing top deviators, each represented in a 
        dictionary: {'url': url, 'value': deviation_pct, 'keywords': []}
        Sorted by deviation pct, optionally absolute.
        """
        deviators = []
        
        start = self._start_time
        boundary = self._boundary_time
        end = self._end_time

        historic = self._storage.get_hitcounts(start_time=start, 
                                               end_time=boundary)
        recent = self._storage.get_hitcounts(start_time=boundary, end_time=end)
        historic_length = boundary - start
        recent_length = end - boundary

        for url, recent_value in recent.iteritems():
            historic_value = historic.get(url, 0.0)
            if not historic_value:
                continue
            recent_hps = recent_value / float(recent_length)
            historic_hps = historic_value / float(historic_length)
            deviation_pct = int((recent_hps - historic_hps) / historic_hps *
                                100)
            keywords = self._storage.get_keywords(url)
            deviators.append({'url':url, 'value':deviation_pct, 
                              'keywords':keywords})
        
        # Reverse sort by deviation pct value
        if sort_absolute:
            deviators.sort(key=lambda x: abs(x['value']), reverse=True)
        else:
            deviators.sort(key=lambda x: x['value'], reverse=True)

        if limit is None:
            return deviators
        else:
            return deviators[:limit]


    def get_keyword_cloud(self, minimum_count=None, limit=50,
                          minimum_pct=0, maximum_pct=100):
        """Returns a dictionary of keywords and their size relative to the
        others, as a percentage with set bounds. Sorted alphabetically.
        """
        cloud = []

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
            cloud.append((keyword, round(pct)))

        return cloud


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
