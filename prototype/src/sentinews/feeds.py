from datetime import datetime

class Feed(object):

	def __init__(self, id, url, lastupdated):
		self.id = id
		self.url = url
		self.lastupdated = lastupdated


	def to_dict(self):

		return {'id': self.id, 'url': self.url, 'lastupdated': self.lastupdated}


	def __repr__(self):
		return 'Feed(%s, %s, %s)' % (self.id, self.url,
			self.lastupdated.strftime("%Y-%m-%d %H:%M:%S"))