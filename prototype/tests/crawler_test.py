# -*- coding: utf-8 -*-
import unittest
from src.sentinews.news_crawler.cnn_parser import CNNParser
from src.sentinews.news_crawler.cnn_crawler import CNNCrawler
from src.sentinews.news_entry import NewsEntry
from src.sentinews.news_crawler.news_crawler import NewsCrawler

class TestCrawler(unittest.TestCase):
    
    def testParser(self):
        url = ("http://cnnespanol.cnn.com/2014/08/31/"
               "tres-estudiantes-chilenos-crean-la-primera-bicicleta-imposible-de-robar/")
        parsed_entry = CNNParser().parse(url)
        self.assertEquals(parsed_entry.source, url)
        self.assertIn("Deportes", parsed_entry.tags)
        self.assertTrue(parsed_entry.content != "")
        self.assertEquals(parsed_entry.title, ("Tres estudiantes chilenos crean la primera bicicleta"
        	                                   " imposible de robar"))

    # def testCrawler(self):
    # 	CNNCrawler().crawl()

    def test(self):
      from src.sentinews.news_rewriter import NewsRewriter

      url = ("http://cnnespanol.cnn.com/2014/09/04/ryder-cup-stephen-gallacher-ian-poulter-y-lee-westwood-los-comodines-del-torneo/")
      parsed_entry = CNNParser().parse(url)
      c = NewsRewriter(parsed_entry)
      c.rewrite()
      c.publish()

if __name__ == '__main__':
    unittest.main()
