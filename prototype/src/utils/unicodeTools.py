

def safe_unicode(text):
    if isinstance(text, unicode):
        u_text = text
    else:
        try:
            u_text = unicode(text, 'utf-8', errors='ignore')
        except Exception, e:
            u_text = text

    return u_text

def safe_unicode_list(list):
    u_list = []
    for string in list:
        u_list.append(self.safe_unicode(string))

    return u_list