# -*- coding: utf-8 -*-
import unittest
from src.sentinews.news_crawler.cnn_parser import CNNParser
from src.sentinews.news_crawler.cnn_crawler import CNNCrawler
from src.sentinews.news_entry import NewsEntry
from src.sentinews.news_crawler.news_crawler import NewsCrawler
from bs4 import BeautifulSoup
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry

class TestCrawler(unittest.TestCase):
    
    def testParser(self):
        url = ("http://cnnespanol.cnn.com/2014/08/31/"
               "tres-estudiantes-chilenos-crean-la-primera-bicicleta-imposible-de-robar/")
        parsed_entry = CNNParser().parse(url)
        self.assertEquals(parsed_entry.source, u'CNN en espa\xf1ol')
        self.assertIn("Deportes", parsed_entry.tags)
        self.assertTrue(parsed_entry.content != "")
        self.assertEquals(parsed_entry.title, ("Tres estudiantes chilenos crean la primera bicicleta"
        	                                   " imposible de robar"))
    def testRemoveCNN(self):
        url = ("http://cnnespanol.cnn.com/2014/09/11/sobrevivientes-del-11-de-septiembre-piden-extension-"
               "del-programa-de-salud/")
        soup = BeautifulSoup(urlopen(url).read())
        top = soup.findAll('div' , { "class" : "cnnRightPost" })[0]
        text = CNNParser()._remove_cnn_header(top.find('div').text)
        self.assertEquals(text[:7], u"Después")

        url = ("http://cnnespanol.cnn.com/2014/09/15/el-huracan-odile-toca-tierra"
               "-y-avanza-hacia-la-paz-baja-california-sur/")
        
        soup = BeautifulSoup(urlopen(url).read())
        top = soup.findAll('div' , { "class" : "cnnRightPost" })[0]
        text = CNNParser()._remove_cnn_header(top.find('div').text)
        self.assertEquals(text[:10], u"El huracán")

    def testFilterEntries(self):
        test_title = 'Al menos 44 muertos al derrumbarse un edificio de una iglesia en Nigeria'
        entries = [{'title': test_title},
                   {'title':'Test entry'}]
        crawler = CNNCrawler()
        filtered_entries = crawler._filter_entries(entries)
        self.assertEquals(len(filtered_entries), 1)
        self.assertEquals(filtered_entries[0]['title'], 'Test entry')

    def testFilterTags(self):
        entries = [NewsEntry('','',['tag1', 'tag2'],''),
                   NewsEntry('','',['tag1', 'tag2', 'Al Galope'],''),
                   NewsEntry('','',['Al Galope'],''),
                   NewsEntry('','',['Héroes de CNN', 'Al Galope'],''),
                   NewsEntry('','',['Héroes de CNN'],''),
                   NewsEntry('','',[],'')]
        crawler = CNNCrawler()
        filtered_entries = crawler._filter_by_tag(entries)
        self.assertEquals(len(filtered_entries), 2)

    # def testCrawler(self):
    # 	CNNCrawler().crawl()
# http://cnnespanol.cnn.com/2014/09/09/bill-murray-dice-cuales-actrices-serian-las-mejores-cazafantasmas/
if __name__ == '__main__':
    unittest.main()
