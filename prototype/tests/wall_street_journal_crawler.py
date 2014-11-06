import unittest
from bs4 import BeautifulSoup
from urllib import urlopen

class TestWallStreetCrawler(unittest.TestCase):

	def test_get_page_url(self):
		url = "http://online.wsj.com/public/page/espanol-inicio.html"
		soup = BeautifulSoup(urlopen(url).read())
		new_elements = soup.findAll('li' , { "class" : "firstList listFirst" })[0]
		self.assertTrue(new_elements is not None)
		self.assertEquals(len(new_elements), 4)




if __name__ == '__main__':
	unittest.main()