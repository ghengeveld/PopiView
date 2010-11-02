class HTMLParser(object):

    def __init__(self):
        self.escapetable = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;"
        }

    def escape(self, text):
        return "".join(self.escapetable.get(c,c) for c in text)
