import unittest
import feedparser
from src.sentinews.parsers.bbc_parser import BBCParser
import traceback

feed_url = 'http://www.bbc.co.uk/mundo/temas/america_latina/index.xml'


class BBCParserTest(unittest.TestCase):

    def test_parse_one_feed(self):
        feeds = feedparser.parse('http://www.bbc.co.uk/mundo/temas/america_latina/index.xml')
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def _test_parse_single_url(self):
        url = 'http://www.bbc.co.uk/mundo/noticias/2015/04/150428_mexico_esclavitud_tintoreria_relato_zunduri_jp'
        # url = 'http://www.bbc.co.uk/mundo/ultimas_noticias/2015/04/150428_chile_bachelet_nueva_constitucion_lav'
        url = 'http://www.bbc.co.uk/mundo/noticias/2015/05/150422_colombia_anori_minas_antipersonales_convivir_nc'

        entry = BBCParser().parse(url=url, tags=['america'])  # Must provide hardcoded tags
        self.assertIsNotNone(entry)
        print("Content:", entry.content, '\n')
        print("Tags:", entry.tags, '\n')
        print("Title:", entry.title, '\n')
        print("Source:", entry.source, '\n')
        print("Category:", entry.categories, '\n')
        print("original_categories:", entry.original_categories, '\n')

    def parse_single_url(self, url):

        entry = BBCParser().parse(url=url, tags=['america'])  # Must provide hardcoded tags
        if '/video_fotos/' in url:
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

if __name__ == '__main__':
    unittest.main()