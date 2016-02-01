import unittest
import feedparser
import traceback
from src.sentinews.parsers.miamidiario_parser import MiamiDiarioParser

feed_url = 'http://www.miamidiario.com/rss/'


class MiamiDiarioParserTest(unittest.TestCase):
    def _test_parse_one_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def parse_single_url(self, url):
        entry = MiamiDiarioParser().parse(url=url)
        if not MiamiDiarioParser().is_parseable(url):
            print "Only parsing certain news"
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

        if len(entries) > 50:
            entries = entries[:50]

        for entry in entries:
            print u"case:", entry['link'], u"\n"
            try:
                self.parse_single_url(entry['link'])
            except Exception as e:
                error_urls.append(entry['link'])
                print "Error parsing"
                print e.message
                print traceback.format_exc()

        print "Total cases: ", len(entries)
        print "Errors", len(error_urls)
        print "Urls:", error_urls

    def _test_parse_single_url(self):
        # TODO: url = ''
        entry = MiamiDiarioParser().parse(url=url)

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