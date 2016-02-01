import unittest
import feedparser
from src.sentinews.parsers.abc_parser import ABCParser

feed_url = 'http://www.abc.es/rss/feeds/abc_ultima.xml'


class ABCParserTest(unittest.TestCase):
    def _test_parse_one_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def parse_single_url(self, url):
        entry = ABCParser().parse(url=url)
        if u'/silencio-por-favor/' in url:
            print "Not parsing silencio-por-favor news"
            self.assertIsNone(entry)
        else:
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

    def _test_parse_single_url(self):
        url = 'http://www.abc.es/internacional/20150504/abci-votacion-cambio-electoral-italia-201505041501.html'
        url = 'http://www.abc.es/economia/20150504/abci-belgica-prepara-inspectores-para-201505041501.html'
        url = 'http://www.abc.es/economia/20150504/abci-belgica-prepara-inspectores-para-201505041501.html?utm_source=abc&utm_medium=rss&utm_content=uh-rss&utm_campaign=traffic-rss'
        url = 'http://sevilla.abc.es/andalucia/20150505/sevi-moreno-diaz-hizo-gazpacho-201505051724.html'
        url = 'http://www.abc.es/madrid/20150506/abci-andradas-carrillo-elecciones-complutense-201505052357.html'

        entry = ABCParser().parse(url=url)

        if u'/silencio-por-favor/' in url:
            print "Nor parsing opinion news"
            self.assertIsNone(entry)
        else:
            self.assertIsNotNone(entry)
            print "Content:", entry.content, '\n'
            print "Tags:", entry.tags, '\n'
            print "Title:", entry.title, '\n'
            print "Source:", entry.source, '\n'
            print "Category:", entry.categories, '\n'
            print "original_categories:", entry.original_categories, '\n'

if __name__ == '__main__':
    unittest.main()