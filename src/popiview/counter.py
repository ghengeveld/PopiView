class Counter(dict):

    def __init__(self, items=None):
        dict.__init__(self)
        if items is not None:
            self.update(items)
    
    def update(self, items):
        for item in items:
            self[item] = self.get(item, 0) +1
        return self
