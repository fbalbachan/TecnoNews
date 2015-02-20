

class Feed(object):
    def __init__(self, id_string, url, parser, last_updated, default_tags=None):
        self.id = id_string
        self.url = url,
        self.parser = parser
        self.last_updated = last_updated
        self.default_tags = default_tags


    def to_dict(self):
        return {'id': self.id, 'url': self.url, 'parser': self.parser,
                'lastupdated': self.last_updated, 'default_tags': self.default_tags}


    def __repr__(self):
        return 'Feed(%s, %s, %s, %s, %s)' % (self.id, self.url, self.parser,
                                             self.last_updated.strftime("%Y-%m-%d %H:%M:%S"),
                                             str(self.default_tags))