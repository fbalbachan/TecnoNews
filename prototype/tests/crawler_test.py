import unittest
from src.sentinews.crawler import Crawler

class CrawlerTest(unittest.TestCase):
	
	crawler = Crawler()

	def test_crawl_cnn(self):
		url = 'http://cnnespanol.cnn.com/feed/'
		entries = self.crawler.crawl('cnn_parser.CNNParser', url)
		self.assertIsNotNone(entries)
		self.assertTrue(len(entries) > 0)
		for entry in entries:
			print entry.title


	def test_crawl_elpais(self):
		url = 'http://ep00.epimg.net/rss/elpais/portada_america.xml'
		entries = self.crawler.crawl('elpais_parser.ElPaisParser', url)
		self.assertIsNotNone(entries)
		self.assertTrue(len(entries) > 0)
		for entry in entries:
			print entry.title


	def test_crawl_euro(self):
		url = 'http://feeds.feedburner.com/euronews/es/news/'
		entries = self.crawler.crawl('euronews_parser.EuroNewsParser', url)
		self.assertIsNotNone(entries)
		self.assertTrue(len(entries) > 0)
		for entry in entries:
			print entry.title


	def test_crawl_bbc_america(self):
		url = 'http://www.bbc.co.uk/mundo/temas/america_latina/index.xml'
		entries = self.crawler.crawl('bbc_parser.BBCParser', url, ['america'])
		self.assertIsNotNone(entries)
		self.assertTrue(len(entries) > 0)
		for entry in entries:
			print entry.title


if __name__ == '__main__':
	unittest.main()