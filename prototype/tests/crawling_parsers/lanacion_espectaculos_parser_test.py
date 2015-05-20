import traceback
import unittest
import feedparser
from src.sentinews.parsers.lanacion_espectaculos_parser import LaNacionEspectaculosParser

feed_url = 'http://servicios.lanacion.com.ar/herramientas/rss/categoria_id=120'


class LaNacionEspectaculosParserTest(unittest.TestCase):
    def _test_parse_one_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def parse_single_url(self, url):
        entry = LaNacionEspectaculosParser().parse(url=url)
        if not LaNacionEspectaculosParser().is_parseable_case(url):
            print "only parssing selected kind of news"
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
            print u"case:", entry['id'], u"\n"
            try:
                self.parse_single_url(url=entry['id'])
            except Exception as e:
                error_urls.append(entry['id'])
                print "Error parsing"
                print e.message
                print traceback.format_exc()

        print "Total cases: ", len(entries)
        print "Errors", len(error_urls)
        print "Urls:", error_urls

    def _test_parse_single_url(self):
        url = 'http://personajes.lanacion.com.ar/1794128-adriana-lima-vs-irina-shayk-duelo-de-diosas-en-cannes'
        url = 'http://servicios.lanacion.com.ar/herramientas/rss/1793847-joaquin-furriel-soy-un-actor-que-logro-tener-su-identidad'
        # entry = LaNacionEspectaculosParser().parse(url=url)
        self.parse_single_url(url)

        # if not LaNacionEspectaculosParser().is_parseable_case(url):
        #     print "Nor parsing this kind of news"
        #     self.assertIsNone(entry)
        # else:
        #     self.assertIsNotNone(entry)
        #     print "Content:", entry.content, '\n'
        #     print "Tags:", entry.tags, '\n'
        #     print "Title:", entry.title, '\n'
        #     print "Source:", entry.source, '\n'
        #     print "Category:", entry.categories, '\n'
        #     print "original_categories:", entry.original_categories, '\n'

if __name__ == '__main__':
    unittest.main()