# -*- coding: utf-8 -*-
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler import NewsCrawler
from src.utils.logger_utils import *
import traceback
from datetime import datetime
from src.sentinews.parsers import cnn_parser
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

    def _test_end_2_end(self):
        link = "http://cnnespanol.cnn.com/2014/09/22/policia-investiga-ataques-racistas-contra-mario-balotelli-tras-un-tuit-del-futbolista/"
        link2 = 'http://cnnespanol.cnn.com/2015/01/06/una-familia-llora-la-perdida-de-siete-seres-queridos-en-el-vuelo-de-airasia/'
        cnnparser = cnn_parser.CNNParser()
        print "after parser instanciate"
        # related_news = self.service.get_list({'wp_id': {'$ne': None}}, 1)
        related_news = []
        #self.assertTrue(len(related_news) == 1)

        self.assertIsNotNone(related_news)

        self.news_entry = cnnparser.parse(url=link2, limit=1)

        self.news_entry.set_related_news(related_news)
        self.news_entry.set_news_versions(related_news)

        c = NewsRewriter(self.news_entry)
        self.assertTrue(len(c.rewritten_entry.versions) > 0)
        self.assertTrue(len(c.rewritten_entry.related) > 0)
        #c.rewrite()
        #be carefull to have a news entry on the collection properly before start

        # c.publish()

        self.news_entry.wp_id = c.rewritten_entry.wp_id
        self.object_id = self.service.save(self.news_entry)

        unmarshalled_entry = self.service.get_list({'_id': self.object_id})[0]
        self.assertIsNotNone(unmarshalled_entry)
        self.assertEquals(unmarshalled_entry.wp_url[:12], "http://tecno")


    def _test_crawl_entire_source(self):

        self.service.remove_all()

        entries = Crawler().crawl('cnn_parser.CNNParser', 'http://cnnespanol.cnn.com/feed/')
        self.assertIsNotNone(entries)
        self.assertTrue(len(entries) > 0)
        for entry in entries:
            related_news = self.service.get_list({'wp_id': {'$ne': None}}, 1)
            entry.set_related_news(related_news)
            entry.set_news_versions(related_news)
            c = NewsRewriter(entry)
            c.publish()
            entry.wp_id = c.rewritten_entry.wp_id
            entry.published_date = datetime.utcnow()
            object_id = self.service.save(entry)
            self.assertIsNotNone(object_id)

    def test_crawl_all_sources(self):

        self.service.remove_all()

        entries = NewsCrawler().crawl_all()
        self.assertIsNotNone(entries)
        self.assertTrue(len(entries) > 0)
        for entry in entries:
            related_news = self.service.get_list({'wp_id': {'$ne': None}}, 1)
            entry.set_related_news(related_news)
            entry.set_news_versions(related_news)
            c = NewsRewriter(entry)
            # c.publish() Must guarantee we use the test config to run this
            entry.wp_id = c.rewritten_entry.wp_id
            entry.published_date = datetime.utcnow()
            object_id = self.service.save(entry)
            self.assertIsNotNone(object_id)


if __name__ == '__main__':
    unittest.main()