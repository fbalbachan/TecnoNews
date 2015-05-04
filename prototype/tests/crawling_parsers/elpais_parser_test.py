import unittest
from src.sentinews.parsers.elpais_parser import ElPaisParser
import feedparser

feed_url = 'http://ep00.epimg.net/rss/elpais/portada_america.xml'


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

    def test_resumen_del_dia(self):
        url = 'http://elpais.com/elpais/2015/05/01/actualidad/1430515195_553826.html'

        entry = ElPaisParser().parse(url=url)
        self.assertIsNone(entry)

    def _test_parse_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        for entry in entries:
            # print entry['link']
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def parse_single_url(self, url):

        entry = ElPaisParser().parse(url=url)
        self.assertIsNotNone(entry)
        print "Content:", entry.content, '\n'
        print "Tags:", entry.tags, '\n'
        print "Title:", entry.title, '\n'
        print "Source:", entry.source, '\n'
        print "Category:", entry.categories, '\n'
        print "original_categories:", entry.original_categories, '\n'

    def test_all_in_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        error_urls = []

        for entry in entries:
            print u"case:", entry['link'], u"\n"
            try:
                self.parse_single_url(entry['link'])
            except Exception as e:
                error_urls.append(entry['link'])

                print "Error parsing"
                print e.message

        print "Total cases: ", len(entries)
        print "Errors", len(error_urls)
        print "Urls:", error_urls

if __name__ == '__main__':
    unittest.main()
