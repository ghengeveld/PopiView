class StorageFilters(object):    
    
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

    def filter_keywords(self, conf):
        """Returns a filter function for filtering keywords.
        """
        ignorelist = []
        for item in conf['keyword_ignorelist'].split(','):
            ignorelist.append(item.strip())
        def filter_function((keyword, count),):
            """Return False if keyword is shorter than 3 characters, in ignore 
            list or numeric.
            """
            if len(keyword) < 3:
                return False
            if keyword in ignorelist:
                return False
            try:
                i = float(keyword)
            except ValueError:
                return True
            else:
                return False
            return True
        return filter_function

    def filter_path(self, path):
        """Return False if path is in ignore list, True otherwise.
        """
        ignorelist = ['','/','/index.php']
        if path in ignorelist:
            return False
        return True

    def filter_sources(self, sources):
        def filter_function(item):
            types = ['direct', 'internal', 'external', 'searches']
            for sourcetype in types:
                if item['source'].startswith(sourcetype):
                    return bool(sources[sourcetype])
            return False
        return filter_function
