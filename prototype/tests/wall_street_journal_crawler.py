import unittest
from bs4 import BeautifulSoup
from urllib import urlopen
from src.sentinews.news_crawler.wall_street_parser import WallStreetParser

class TestWallStreetCrawler(unittest.TestCase):

	def test_get_page_url(self):
		url = "http://online.wsj.com/public/page/espanol-inicio.html"
		soup = BeautifulSoup(urlopen(url).read())
		new_elements = soup.findAll('li' , { "class" : "firstList listFirst" })[0]
		self.assertTrue(new_elements is not None)
		self.assertEquals(len(new_elements), 4)


	def test_create_newWallStreetEntry(self):
		wall_street_p = WallStreetParser()
		ws_entry = wall_street_p.parse('http://online.wsj.com/public/page/espanol-inicio.html')
		self.assertEquals(ws_entry.title,'')
		self.assertEquals(ws_entry.content,'')
		self.assertEquals(len(ws_entry.tags), 0)
		self.assertEquals(ws_entry.source, u'Wall Street Journal')


if __name__ == '__main__':
	unittest.main()