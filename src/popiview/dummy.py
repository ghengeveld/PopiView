import time
from math import floor
from popiview.hit import Hit

class Dummy(object):

    
    def __init__(self, storage):
        self._storage = storage
        self._storage.clear_hits()

    
    def create_hits_evenly(self, url, referrer=None, num=100, 
                           min_time=1285040000, max_time=1285090000):
        time = min_time
        time_separator = floor((max_time - min_time) / num)
        while num > 0:
            self._storage.add_hit(Hit(url, timestamp=time, referrer=referrer))
            time = time + time_separator
            num -= 1


    def create_hits_linear(self, url, referrer=None, 
                           start_hits_per_hour=100, end_hits_per_hour=100, 
                           start_time=None, end_time=None):
        start_hits_per_second = start_hits_per_hour / 3600.0
        end_hits_per_second = end_hits_per_hour / 3600.0
        now = time.time()
        
        if start_time is None:
            start_time = now - 3600 * 24
        if end_time is None:
            end_time = now

        seconds = int(end_time - start_time)
        decimal = 0.0
        
        for i in range(0, seconds):
            num_hits = start_hits_per_second + i/float(seconds) * (
                       end_hits_per_second - start_hits_per_second)

            decimal += num_hits % 1
            if decimal >= 1.0:
                decimal -= 1.0
                num_hits += 1.0

            for j in range(0, int(num_hits)):
                ts = start_time + i
                self._storage.add_hit(Hit(url, timestamp=ts, referrer=referrer))
