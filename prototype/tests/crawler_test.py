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
      entries =  NewsCrawler().crawl_all()
      print 'entries', len(entries)
      for entry in entries:
        try:
          c = NewsRewriter(entry)
          c.rewrite()
          c.publish()
        except Exception, e:
          print str(e)
          continue
if __name__ == '__main__':
    unittest.main()
