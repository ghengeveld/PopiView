class View(object):

    def __init__(self):
        pass


    def index(self):
        with open('views/index.html') as f:
            content = f.read()
        return content
