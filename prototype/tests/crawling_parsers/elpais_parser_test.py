import unittest
from src.sentinews.parsers.elpais_parser import ElPaisParser
import feedparser


class TestElPaisCrawler(unittest.TestCase):
    def test_create_single_entry(self):
        url = 'http://internacional.elpais.com/internacional/2015/01/19/actualidad/1421702003_489797.html'
        # url = 'http://elpais.com/economia/2015/04/29/actualidad/1430319380_380989.html?ref=rss&format=simple&link=link'
        # url = 'http://elpais.com/internacional/2015/04/26/actualidad/1430030012_980448.html?ref=rss&format=simple&link=link'
        # url = 'http://elpais.com/internacional/2015/04/29/actualidad/1430275689_192239.html?ref=rss&format=simple&link=link'
        # url = 'http://elpais.com/economia/2015/04/29/actualidad/1430288283_141064.html?ref=rss&format=simple&link=link'
        # url = 'http://elpais.com/elpais/2015/03/12/planeta_futuro/1426162513_243474.html?ref=rss&format=simple&link=link'
        # url = 'http://elpais.com/internacional/2015/04/29/actualidad/1430329478_572194.html?ref=rss&format=simple&link=link'

        entry = ElPaisParser().parse(url=url)
        self.assertIsNotNone(entry)
        print "Content:", entry.content, '\n'
        print "Tags:", entry.tags, '\n'
        print "Title:", entry.title, '\n'
        print "Source:", entry.source, '\n'
        print "Category:", entry.categories, '\n'
        print "original_categories:", entry.original_categories, '\n'

    def test_parse_feed(self):
        feeds = feedparser.parse('http://ep00.epimg.net/rss/elpais/portada_america.xml')
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        for entry in entries:
            # print entry['link']
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)



if __name__ == '__main__':
    unittest.main()
