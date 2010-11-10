def get_unicode(string):
    if isinstance(string, unicode) or string is None:
        return string
    coding_options = ['utf-8', 'latin-1']
    for coding in coding_options:
        try:
            return string.decode(coding)
        except:
            continue
    return string.decode('utf-8', 'ignore')
