import unittest
from src.sentinews.crawler import Crawler
from src.utils.sanitize import Sanitizer

class CrawlerTest(unittest.TestCase):
	
	crawler = Crawler()
	sanitizer = Sanitizer()

	def test_crawl_cnn(self):
		url = 'http://cnnespanol.cnn.com/feed/'
		entries = self.crawler.crawl('cnn_parser.CNNParser', url)
		self.assertIsNotNone(entries)
		self.assertTrue(len(entries) > 0)
		for entry in entries:
			print entry.title


	def test_crawl_elpais(self):
		url = 'http://ep00.epimg.net/rss/tags/ultimas_noticias.xml'
		entries = self.crawler.crawl('elpais_parser.ElPaisParser', url)
		self.assertIsNotNone(entries)
		self.assertTrue(len(entries) > 0)
		for entry in entries:
			entry.content = self.sanitizer.process_content(entry.content)
			self.assertEquals(entry.content)
			print entry.title


	def test_crawl_euro(self):
		url = 'http://feeds.feedburner.com/euronews/es/news/'
		entries = self.crawler.crawl('euronews_parser.EuroNewsParser', url)
		self.assertIsNotNone(entries)
		self.assertTrue(len(entries) > 0)
		for entry in entries:
			entry.content = self.sanitizer.process_content(entry.content)
			self.assertEquals(entry.content)
			print entry.title
			

	def test_crawl_bbc_america(self):
		url = 'http://www.bbc.co.uk/mundo/temas/america_latina/index.xml'
		entries = self.crawler.crawl('bbc_parser.BBCParser', url, ['america'])
		self.assertIsNotNone(entries)
		self.assertTrue(len(entries) > 0)
		help(self.sanitizer)
		for entry in entries:
			entry.content = self.sanitizer.process_content(entry.content)
			self.assertEquals(entry.content)
			print entry.title


if __name__ == '__main__':
	unittest.main()