import unittest
import feedparser
from src.sentinews.parsers.euronews_parser import EuroNewsParser


class TestEuroNewsCrawler(unittest.TestCase):
    base_path = 'http://es.euronews.com'

    def test_parse_one_feed(self):
        feed_url = 'http://feeds.feedburner.com/euronews/es/news?format=xml'
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            print entry['link']
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def test_create_single_entry(self):
        url = 'http://feedproxy.google.com/~r/euronews/es/news/~3/FUB5K4A2XRU/'
        url = 'http://feedproxy.google.com/~r/euronews/es/news/~3/sk6_HcTD6bY/'
        url = 'http://feedproxy.google.com/~r/euronews/es/news/~3/Ud5TrEezt1g/'
        entry = EuroNewsParser().parse(url)
        self.assertIsNotNone(entry)
        print "Content:", entry.content, '\n'
        print "Tags:", entry.tags, '\n'
        print "Title:", entry.title, '\n'
        print "Source:", entry.source, '\n'
        print "Category:", entry.categories, '\n'
        print "original_categories:", entry.original_categories, '\n'

if __name__ == '__main__':
    unittest.main()