import unittest
from bs4 import BeautifulSoup
from urllib2 import urlopen, Request
from src.sentinews.news_crawler.elpais_parser import ElPaisParser
from src.sentinews.news_crawler.elpais_crawler import ElPaisCrawler
from src.sentinews.news_entry import NewsEntry


class TestElPaisCrawler(unittest.TestCase):

	def test_create_single_entry(self):
		new_entries = ElPaisParser().parse('http://elpais.com/tag/fecha/hoy')
		self.assertTrue(new_entries is not None)
		self.assertTrue(len(new_entries) == 1)
		self.assertTrue(len(new_entries[0].title)>1)
		self.assertTrue(len(new_entries[0].content)>1)
		print new_entries[0].tags
		print new_entries[0].title
		self.assertTrue(len(new_entries[0].tags) > 1)


	def test_entries_list(self):
		new_entries = ElPaisParser().parse('http://elpais.com/tag/fecha/hoy',4)
		self.assertTrue(new_entries is not None)
		print len(new_entries)
		self.assertTrue(len(new_entries) == 4)


	def test_filtered_entries_list(self):
		new_entries_filtered = ElPaisCrawler().crawl()
		self.assertTrue(new_entries_filtered is not None)
		self.assertTrue(len(new_entries_filtered) == 4)


if __name__ == '__main__':
	unittest.main()
