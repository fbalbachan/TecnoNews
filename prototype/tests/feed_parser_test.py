import unittest
import feedparser

class FeedParserTest(unittest.TestCase):

	univision_feed_url = 'http://feedsyn.univision.com/lo-ultimo-de-univision'


	def test_parse_univision(self):
		feeds = feedparser.parse(self.univision_feed_url)
		entries = feeds['entries']
		self.assertIsNotNone(feeds)
		self.assertTrue(len(feeds))
		print len(feeds)
		for entry in entries:
			self.assertTrue(len(entry['link']) > 0)
			print entry['link']
		for entry in entries:
			self.assertTrue(len(entry['title']) > 0)
			print entry['title']
		for entry in entries:
			self.assertTrue(len(entry['description']) > 0)
			print entry['description']


	def test_parse_elpais(self):
		pass


	def test_parse_euronews(self):
		pass

if __name__ == '__main__':
	unittest.main()