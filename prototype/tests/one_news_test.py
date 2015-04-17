# -*- coding: utf-8 -*-
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler import NewsCrawler
from src.utils.logger_utils import *
import traceback
from datetime import datetime
from src.sentinews.parsers import bbc_parser, cnn_parser
import wikipedia as wk
import unittest
from src.services.mongodb.news_entries_service import NewsEntriesService
from bson.objectid import ObjectId
from src.sentinews.crawler import Crawler


class TecnonewsTest(unittest.TestCase):
    ''' Clase para testear una sola noticia end to end '''
    service = NewsEntriesService()
    news_entry = None
    object_id = None

    def test_end_2_end(self):
        # TODO: Complete
        link = "http://cnnespanol.cnn.com/2014/09/22/policia-investiga-ataques-racistas-contra-mario-balotelli-tras-un-tuit-del-futbolista/"
        link2 = 'http://cnnespanol.cnn.com/2015/04/14/el-pequeno-paraiso-insular-en-el-que-la-gente-respira-musica/'
        link3 = 'http://www.bbc.co.uk/mundo/ultimas_noticias/2015/04/150412_ultnot_colombia_falsos_positivos_generales_fp'
        # parser = bbc_parser.BBCParser()
        parser = cnn_parser.CNNParser()
        # related_news = self.service.get_list({'wp_id': {'$ne': None}}, 1)
        related_news = []

        # self.assertIsNotNone(related_news)
        print self.news_entry
        self.news_entry = parser.parse(url=link2)
        # self.news_entry = parser.parse(url=link3, tags=['america'])
        print self.news_entry

        self.news_entry.set_related_news(related_news)
        self.news_entry.set_news_versions(related_news)


        rewriter = NewsRewriter(self.news_entry)
        rewriter.rewritten_entry.other_versions = []
        rewriter.rewrite_content()

        # self.assertTrue(len(c.rewritten_entry.versions) > 0)
        # self.assertTrue(len(c.rewritten_entry.related) > 0)
        #c.rewrite()
        #be carefull to have a news entry on the collection properly before start

        # c.publish()

        # self.news_entry.wp_id = c.rewritten_entry.wp_id
        # self.object_id = self.service.save(self.news_entry)
        #
        # unmarshalled_entry = self.service.get_list({'_id': self.object_id})[0]
        # self.assertIsNotNone(unmarshalled_entry)
        # self.assertEquals(unmarshalled_entry.wp_url[:12], "http://tecno")

if __name__ == '__main__':
    unittest.main()