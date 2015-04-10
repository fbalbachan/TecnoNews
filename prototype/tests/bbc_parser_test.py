import unittest
import feedparser
from bs4 import BeautifulSoup
from urllib2 import urlopen


class BBCParserTest(unittest.TestCase):
    def test_parse_one_feed(self):
        feeds = feedparser.parse('http://www.bbc.co.uk/mundo/temas/america_latina/index.xml')
        self.assertIsNotNone(feeds)
        entries = feeds['entries']
        self.assertIsNotNone(entries)
        for entry in entries:
            self.assertIsNotNone(entry['link'])
            self.assertTrue(len(entry['link']) > 0)

    def test_parse_single_url(self):
        url = 'http://www.bbc.co.uk/mundo/ultimas_noticias/2015/01/150122_ultnot_chile_carabineros_muertes_peru_az'
        soup = BeautifulSoup(urlopen(url))
        self.assertIsNotNone(soup)
        article = soup.find('div', {'class': 'story-body'})
        self.assertIsNotNone(article)
        title = article.find('h1', {'class': 'story-body__h1'}).text
        self.assertIsNotNone(title)
        self.assertTrue(len(title) > 0)
        paragraphs = article.find('div', {'class': 'story-body__inner'}).find_all('p')
        self.assertIsNotNone(paragraphs)
        self.assertTrue(len(paragraphs) > 0)
        for paragraph in paragraphs:
            self.assertTrue(len(paragraph.text) > 0)

        content = ' '.join([paragraph.text + '\n' for paragraph in paragraphs])
        self.assertIsNotNone(content)
        print content


if __name__ == '__main__':
    unittest.main()