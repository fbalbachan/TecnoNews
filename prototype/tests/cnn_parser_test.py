import unittest
import feedparser
from src.sentinews.parsers.cnn_parser import CNNParser


class CNNParserTest(unittest.TestCase):
    def test_parse_one_feed(self):
        feeds = feedparser.parse('http://cnnespanol.cnn.com/feed/')
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def test_parse_single_url(self):
        url = 'http://cnnespanol.cnn.com/2015/04/17/mike-huckabee-promete-un-anuncio-sobre-2016-para-este-viernes-por-la-noche/'
        url = 'http://cnnespanol.cnn.com/2015/04/08/el-avance-de-isis-en-el-sur-de-siria-una-buena-noticia-para-al-asad/'
        url = 'http://cnnespanol.cnn.com/2015/04/14/police-de-arizona-tramples-of-way-intentional-a-un-suspicious-to-arrest/'
        url = 'http://cnnespanol.cnn.com/2015/04/17/los-planes-de-los-yihadistas-para-las-mujeres/'
        entry = CNNParser().parse(url=url)
        self.assertIsNotNone(entry)
        print "Content:", entry.content, '\n'
        print "Tags:", entry.tags, '\n'
        print "Title:", entry.title, '\n'
        print "Source:", entry.source, '\n'

if __name__ == '__main__':
    unittest.main()