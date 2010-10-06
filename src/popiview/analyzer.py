import time
import operator
import math

class Analyzer(object):


    def __init__(self, storage, start_time=None, boundary_time=None, end_time=None):
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


    def get_top_deviators(self, limit=None, sort_absolute=False):
        deviators = []
        
        start = self._start_time
        boundary = self._boundary_time
        end = self._end_time

        historic = self._storage.get_hitcounts(start_time=start, end_time=boundary)
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
            deviators.append({'url':url, 'value':deviation_pct, 'keywords':keywords})
        
        deviators.sort(key=lambda x: abs(x['value']), reverse=True)

        if limit is None:
            return deviators
        else:
            return deviators[:limit]


    def calc_sd(self, numlist):
        if len(numlist):
            avg = sum(numlist) / len(numlist)
            devs = []
            for num in numlist:
                devs.append((num - avg) ** 2)
            if len(devs):
                return (sum(devs) / len(devs)) ** 0.5
        return 0.0
