import unittest
import feedparser
import traceback
import pdb
from src.sentinews.parsers.nuevoherald_parser import NuevoHeraldParser

feed_url = 'http://www.elnuevoherald.com/?widgetName=rssfeed&widgetContentId=710494&getXmlFeed=true'


class NuevoHeraldParserTest(unittest.TestCase):
    
    def _test_parse_one_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def parse_single_url(self, url):

        entry = NuevoHeraldParser().parse(url=url)
        if not NuevoHeraldParser().is_parseable(url):
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
            # print "keywords:", entry.keywords, '\n'

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

    def _test_parse_single_url(self):
        # TODO: url = ''

        
        entry = NuevoHeraldParser().parse(url=url)
        pdb.set_trace()
        if ('/opinion-es/' in url) or ('/vivir-mejor/' in url):
            print("Not parsing opinion or lifestyle news")
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