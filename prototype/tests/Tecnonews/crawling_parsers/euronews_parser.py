import unittest
import feedparser
from src.sentinews.parsers.euronews_parser import EuroNewsParser

feed_url = 'http://feeds.feedburner.com/euronews/es/news?format=xml'


class TestEuroNewsCrawler(unittest.TestCase):
    base_path = 'http://es.euronews.com'

    def test_parse_one_feed(self):

        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            print entry['link']
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def _test_create_single_entry(self):
        url = 'http://feedproxy.google.com/~r/euronews/es/news/~3/Ud5TrEezt1g/'

        entry = EuroNewsParser().parse(url)
        self.assertIsNotNone(entry)
        print "Content:", entry.content, '\n'
        print "Tags:", entry.tags, '\n'
        print "Title:", entry.title, '\n'
        print "Source:", entry.source, '\n'
        print "Category:", entry.categories, '\n'
        print "original_categories:", entry.original_categories, '\n'

    def parse_single_url(self, url):

        entry = EuroNewsParser().parse(url)
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