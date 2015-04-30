import unittest
import feedparser
from src.sentinews.parsers.bbc_parser import BBCParser


class BBCParserTest(unittest.TestCase):
    def test_parse_one_feed(self):
        feeds = feedparser.parse('http://www.bbc.co.uk/mundo/temas/america_latina/index.xml')
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            print entry['link']
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def test_parse_single_url(self):
        url = 'http://www.bbc.co.uk/mundo/noticias/2015/04/150428_mexico_esclavitud_tintoreria_relato_zunduri_jp'
        # url = 'http://www.bbc.co.uk/mundo/ultimas_noticias/2015/04/150428_chile_bachelet_nueva_constitucion_lav'
        entry = BBCParser().parse(url=url, tags=['america'])  # Must provide hardcoded tags
        self.assertIsNotNone(entry)
        print "Content:", entry.content, '\n'
        print "Tags:", entry.tags, '\n'
        print "Title:", entry.title, '\n'
        print "Source:", entry.source, '\n'
        print "Category:", entry.categories, '\n'
        print "original_categories:", entry.original_categories, '\n'


if __name__ == '__main__':
    unittest.main()