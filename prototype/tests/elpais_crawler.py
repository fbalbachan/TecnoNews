import unittest
from bs4 import BeautifulSoup
from urllib2 import urlopen, Request
from src.sentinews.parsers import *
from src.sentinews.news_entry import NewsEntry
import feedparser


class TestElPaisCrawler(unittest.TestCase):

	def test_create_single_entry(self):
		new_entry = elpais_parser.ElPaisParser().parse('http://internacional.elpais.com/internacional/2015/01/19/actualidad/1421702003_489797.html')
		self.assertTrue(new_entry is not None)
		
		self.assertTrue(new_entry.title>1)
		self.assertTrue(new_entry.content>1)
		print new_entry.tags
		print new_entry.title
		self.assertTrue(len(new_entry.tags) > 1)	

	def test_parse_feed(self):
		feeds = feedparser.parse('http://ep00.epimg.net/rss/elpais/portada_america.xml')
		self.assertIsNotNone(feeds)
		entries = feeds['entries']
		self.assertIsNotNone(feeds)
		self.assertTrue(len(feeds) > 0)


if __name__ == '__main__':
	unittest.main()
