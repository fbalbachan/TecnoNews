import unittest
import feedparser
from src.sentinews.parsers.elmundo_parser import ElMundoParser

feed_url = 'http://www.elmundo.es/rss/portada.xml'


class ElMundoParserTest(unittest.TestCase):
    def _test_parse_one_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def test_parse_single_url(self):
        # url = 'http://www.elmundo.es/internacional/2015/04/28/553f720622601d7f098b456e.html'
        # url = 'http://www.elmundo.es/internacional/2015/04/28/553f9420268e3e10258b4589.html'
        # url = 'http://www.elmundo.es/madrid/2015/04/29/5540d9c7268e3ea1688b457e.html'
        url = 'http://www.elmundo.es/salud/2015/04/29/5540e08bca47415e108b4579.html'
        # url = 'http://www.elmundo.es/opinion/2015/04/29/554138cd22601db75d8b456d.html'

        entry = ElMundoParser().parse(url=url)
        if '/opinion/' in url:
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

    def parse_single_url(self, url):

        entry = ElMundoParser().parse(url=url)
        if '/opinion/' in url:
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




if __name__ == '__main__':
    unittest.main()