import traceback
import unittest
import feedparser
from src.sentinews.parsers.clarin_extrashow_parser import ClarinExtrashowParser

feed_url = 'http://www.clarin.com/rss/extrashow/'


class ClarinExtrashowParserTest(unittest.TestCase):
    def _test_parse_one_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def parse_single_url(self, url):
        entry = ClarinExtrashowParser().parse(url=url)
        if not ClarinExtrashowParser().is_parseable_case(url):
            print("only parssing selected kind of news")
            self.assertIsNone(entry)
        else:

            self.assertIsNotNone(entry)
            print("Content:", entry.content, '\n')
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

    def test_parse_single_url(self):
        url = 'http://www.clarin.com/extrashow/cine/cannes-para-principiantes-mad-max-mingitorios_0_1357064718.html'
        entry = ClarinExtrashowParser().parse(url=url)

        if '/silencio-por-favor/' in url:
            print("Nor parsing opinion news")
            self.assertIsNone(entry)
        else:
            self.assertIsNotNone(entry)
            print("Content:", entry.content, '\n')
            print("Tags:", entry.tags, '\n')
            print("Title:", entry.title, '\n')
            print("Source:", entry.source, '\n')
            print("Category:", entry.categories, '\n')
            print("original_categories:", entry.original_categories, '\n')

if __name__ == '__main__':
    unittest.main()