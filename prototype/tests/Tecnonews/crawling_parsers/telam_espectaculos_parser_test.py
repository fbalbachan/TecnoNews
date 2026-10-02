import unittest
import feedparser
from src.sentinews.parsers.telam_espectaculos_parser import TelamEspectaculosParser

feed_url = 'http://www.telam.com.ar/rss2/espectaculos.xml'


class TelamEspectaculosParserTest(unittest.TestCase):
    def _test_parse_one_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def parse_single_url(self, url):
        entry = TelamEspectaculosParser().parse(url=url)
        if not TelamEspectaculosParser().is_parseable_case(url):
            print("Nor parsing news")
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

        print("Total cases: ", len(entries))
        print("Errors", len(error_urls))
        print("Urls:", error_urls)

    def test_parse_single_url(self):
        url = 'http://www.telam.com.ar/notas/201505/105200-cine-festival-de-cannes-la-patota-santiago-mitre-dolores-fonzi.html'
        if not TelamEspectaculosParser().is_parseable_case(url):
            print("Nor parsing news")
            self.assertIsNone(entry)
        else:
            entry = TelamEspectaculosParser().parse(url=url)
            self.assertIsNotNone(entry)
            print("Content:", entry.content, '\n')
            print("Tags:", entry.tags, '\n')
            print("Title:", entry.title, '\n')
            print("Source:", entry.source, '\n')
            print("Category:", entry.categories, '\n')
            print("original_categories:", entry.original_categories, '\n')

if __name__ == '__main__':
    unittest.main()