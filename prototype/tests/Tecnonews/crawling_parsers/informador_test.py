import unittest
import feedparser
import traceback
from src.sentinews.parsers.informador_parser import InformadorParser

feed_url = 'http://feeds.informador.com.mx/359/estados-unidos.rss'


class InformadorParserTest(unittest.TestCase):
    def _test_parse_one_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def parse_single_url(self, url):
        entry = InformadorParser().parse(url=url)
        if not InformadorParser().is_parseable(url):
            print("Only parsing certain news")
            self.assertIsNone(entry)
        else:
            self.assertIsNotNone(entry)
            print("Content:")
            for paragraph in entry.content.split('\n'):
                print(paragraph + '\n')
            print("Tags:", entry.tags, '\n')
            print("Title:", entry.title, '\n')
            print("Source:", entry.source, '\n')
            print("Category:", entry.categories, '\n')
            print("original_categories:", entry.original_categories, '\n')

    def test_all_in_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        error_urls = []

        if len(entries) > 50:
            entries = entries[:50]

        for entry in entries:
            print("case:", entry['link'], "\n")
            try:
                self.parse_single_url(entry['link'])
            except Exception as e:
                error_urls.append(entry['link'])
                print("Error parsing")
                print(str(e))
                print(traceback.format_exc())

        print("Total cases: ", len(entries))
        print("Errors", len(error_urls))
        print("Urls:", error_urls)

    def _test_parse_single_url(self):
        # TODO: url = ''
        entry = InformadorParser().parse(url=url)

        if '/silencio-por-favor/' in url:
            print("Nor parsing opinion news")
            self.assertIsNone(entry)
        else:
            self.assertIsNotNone(entry)
            print("Content:")
            for paragraph in entry.content.split('\n'):
                print(paragraph + '\n')
            print("Tags:", entry.tags, '\n')
            print("Title:", entry.title, '\n')
            print("Source:", entry.source, '\n')
            print("Category:", entry.categories, '\n')
            print("original_categories:", entry.original_categories, '\n')


if __name__ == '__main__':
    unittest.main()