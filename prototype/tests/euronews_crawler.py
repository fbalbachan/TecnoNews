import unittest
from bs4 import BeautifulSoup
from urllib2 import urlopen, Request
from src.sentinews.news_crawler.euronews_parser import EuroNewsParser
from src.sentinews.news_crawler.euronews_crawler import EuroNewsCrawler
from src.sentinews.news_entry import NewsEntry

class TestEuroNewsCrawler(unittest.TestCase):

	url = 'http://es.euronews.com/noticias/boletin/'
	base_path = 'http://es.euronews.com'

	def test_get_url(self):
		soup = BeautifulSoup(urlopen(self.url).read())
		news_list = soup.find('ul', {'id': 'bulletin-list'})
		self.assertTrue(len(news_list)>1)
		news_elements = news_list.find_all('li')
		self.assertTrue(len(news_elements)>1)
		article = news_elements[0]
		title = article.find('span', {'class': 'bulletin-title'}).text[12:]
		self.assertTrue(title is not None)
		article_url = article.find('a', {'class': 'read-more-button'})['href']
		self.assertTrue(article_url is not None)
		self.assertTrue(len(title)>0)


	def test_create_EuroNews_entry(self):
		soup = BeautifulSoup(urlopen(self.url).read())
		article = soup.find('ul', {'id': 'bulletin-list'}).find('li')
		self.assertTrue(article is not None)
		title = article.find('span', {'class': 'bulletin-title'}).text[12:]
		self.assertTrue(title is not None)
		self.assertTrue(len(title) > 1)
		article_url = article.find('a', {'class': 'read-more-button'})['href']
		self.assertTrue(article_url is not None)
		self.assertTrue(len(article_url) > 1)
		full_url = self.base_path + str(article_url)
		article_soup = BeautifulSoup(urlopen(full_url).read())
		content_paragraphs_list = article_soup.find('div', {'id': 'articleTranscript'})\
		.find_all('p')
		self.assertTrue(content_paragraphs_list is not None)
		self.assertTrue(len(content_paragraphs_list) > 1)

		entry = NewsEntry(title, str(content_paragraphs_list), [], u'euronews')

		self.assertTrue(entry is not None)
		self.assertEquals(entry.title, title)
		self.assertEquals(entry.content, str(content_paragraphs_list))
		self.assertEquals(entry.tags, [])
		self.assertEquals(entry.source, u'euronews')

	def test_create_single_entry(self):
		new_entries = EuroNewsParser().parse('http://es.euronews.com/noticias/boletin/')
		self.assertTrue(new_entries is not None)
		self.assertTrue(len(new_entries) == 1)


	def test_create_list_entries(self):
		new_entries = EuroNewsParser().parse('http://es.euronews.com/noticias/boletin/',5)
		self.assertTrue(new_entries is not None)
		self.assertTrue(len(new_entries) == 5)


	def test_create_filtered_list_entries(self):
		filtered_list = EuroNewsCrawler().crawl()
		self.assertTrue(filtered_list is not None)
		print len(filtered_list)
		print filtered_list[0].source
		print filtered_list[1].source

		self.assertTrue(len(filtered_list) == 5)	


if __name__ == '__main__':
	unittest.main()