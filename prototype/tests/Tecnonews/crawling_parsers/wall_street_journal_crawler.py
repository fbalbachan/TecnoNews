import unittest
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from src.sentinews.news_crawler.wall_street_parser import WallStreetParser
from time import sleep

class TestWallStreetCrawler(unittest.TestCase):

	def test_get_page_url(self):
		headers = { 'User-Agent' : 'Mozilla/5.0' }
		url = "http://online.wsj.com/public/page/actualidad.html"
		req = Request(url, None, headers)
		soup = BeautifulSoup(urlopen(req).read())
		new_elements = soup.findAll('li' , { "class" : "listFirst" })[0]
		self.assertTrue(new_elements is not None)
		self.assertEqual(len(new_elements), 4)

		article_content_url = new_elements.find('h2').find('a')['href']
		sleep(2)
		req = Request(article_content_url, None, headers)
		article = BeautifulSoup(urlopen(req).read())
		self.assertTrue(article is not None)
		print(article)
		content = article.find('article').findAll('p')
		self.assertTrue(content is not None)
		self.assertTrue(len(content) > 0)
		print(article_content_url)
		self.assertTrue(article_content_url is not None)


	def test_create_newWallStreetEntry(self):
		wall_street_p = WallStreetParser()
		ws_entry = wall_street_p.parse('http://online.wsj.com/public/page/actualidad.html')
		self.assertEqual(ws_entry.title,'')
		self.assertEqual(ws_entry.content,'')
		self.assertEqual(len(ws_entry.tags), 0)
		self.assertEqual(ws_entry.source, 'Wall Street Journal')


if __name__ == '__main__':
	unittest.main()