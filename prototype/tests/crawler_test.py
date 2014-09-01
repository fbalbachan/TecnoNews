# -*- coding: utf-8 -*-
import unittest
from src.sentinews.news_crawler.cnn_parser import CNNParser
from src.sentinews.news_entry import NewsEntry

class TestCrawler(unittest.TestCase):
    def test(self):
        import pudb;pu.db
        CNNParser().parse("http://cnnespanol.cnn.com/2014/08/31/tres-estudiantes-chilenos-crean-la-primera-bicicleta-imposible-de-robar/")


if __name__ == '__main__':
    unittest.main()
