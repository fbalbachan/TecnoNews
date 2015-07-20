import unittest
import feedparser
import traceback
from src.sentinews.parsers.diario_americas_parser import DiarioAmericasParser

feed_url = 'http://www.diariolasamericas.com/rss/1_portada/index.rss'


class DiarioAmericasParserTest(unittest.TestCase):
    def _test_parse_one_feed(self):
        feeds = feedparser.parse(feed_url)
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def parse_single_url(self, url):
        entry = DiarioAmericasParser().parse(url=url)
        if not DiarioAmericasParser().is_parseable(url):
            print "Only parsing certain news"
            self.assertIsNone(entry)
        else:
            self.assertIsNotNone(entry)
            print "Content:"
            for paragraph in entry.content.split('\n'):
                print paragraph + '\n'
            print "Tags:", entry.tags, '\n'
            print "Title:", entry.title, '\n'
            print "Source:", entry.source, '\n'
            print "Category:", entry.categories, '\n'
            print "original_categories:", entry.original_categories, '\n'

    def _test_all_in_feed(self):
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

    def test_parse_single_url(self):
        url = 'http://www.diariolasamericas.com/5051_portada-america-latina/3222467_jpmorgan-chase-gana-un-8-5-por-ciento-mas-en-el-primer-semestre-de-2015.html'
        url = 'http://www.diariolasamericas.com/5051_portada-america-latina/3222784_humala-afirma-que-su-esposa-no-teme-a-la-comision-investigadora-del-congreso.html'
	url = 'http://www.diariolasamericas.com/4848_venezuela/3224252_asamblea-nacional-unanime-aprobar-gestion-territorial.html'
        entry = DiarioAmericasParser().parse(url=url)

        if u'/silencio-por-favor/' in url:
            print "Nor parsing opinion news"
            self.assertIsNone(entry)
        else:
            self.assertIsNotNone(entry)
            print "Content:"
            for paragraph in entry.content.split('\n'):
                print paragraph + '\n'
            print "Tags:", entry.tags, '\n'
            print "Title:", entry.title, '\n'
            print "Source:", entry.source, '\n'
            print "Category:", entry.categories, '\n'
            print "original_categories:", entry.original_categories, '\n'

if __name__ == '__main__':
    unittest.main()
