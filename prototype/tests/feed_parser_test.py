import unittest
import feedparser
from src.sentinews.news_crawler import * 

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

	def test_create_class_by_parameter(self):

		def create(cls):
			return cls()

		class_name = 'cnn_parser.CNNParser'
		parser = create(eval(class_name))
		self.assertTrue(isinstance(parser, cnn_parser.CNNParser))



	def test_parse_elpais(self):
		pass


	def test_parse_euronews(self):
		pass

if __name__ == '__main__':
	unittest.main()