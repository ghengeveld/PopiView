import os


class View(object):

    def __init__(self):
        pass


    def index(self):
        index_path = os.path.join(os.path.split(__file__)[0], 
                                  '../../',
                                  'views/index.html')

        with open(index_path) as f:
            content = f.read()
        return content
