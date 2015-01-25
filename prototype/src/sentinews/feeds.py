from datetime import datetime

class Feed(object):

	def __init__(self, id, url, parser, lastupdated, default_tags=None):
		self.id = id
		self.url = url,
		self.parser = parser
		self.lastupdated = lastupdated
		self.default_tags = default_tags


	def to_dict(self):

		return {'id': self.id, 'url': self.url,'parser': self.parser,
		'lastupdated': self.lastupdated, 'default_tags': self.default_tags}


	def __repr__(self):
		return 'Feed(%s, %s, %s, %s, %s)' % (self.id, self.url, self.parser,
			self.lastupdated.strftime("%Y-%m-%d %H:%M:%S"), 
			str(self.default_tags))