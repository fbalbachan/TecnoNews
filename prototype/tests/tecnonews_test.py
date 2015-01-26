# -*- coding: utf-8 -*-
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry

from src.sentinews.news_crawler.news_crawler import NewsCrawler

import traceback
import datetime
from src.sentinews.news_crawler.cnn_parser import CNNParser
import wikipedia as wk
from src.sentinews.news_crawler.cnn_crawler import CNNCrawler
import unittest
from bson.objectid import ObjectId

from src.services.mongodb.news_entries_service import NewsEntriesService
from src.sentinews.news_rewriter import NewsRewriter
from src.utils.logger_utils import *
from src.utils.relatedNewsEntries import RelatedNewsEntries
from src.utils.similarParagraph import SimilarParagraph
import traceback

class TecnonewsTest(unittest.TestCase):
    ''' Clase para testear una sola noticia end to end '''
    service = NewsEntriesService('test')
    news_entry = None
    object_id = None

    def test_end_2_end(self):
        logger = get_logger('tecnonews')
        # link = "http://cnnespanol.cnn.com/2014/09/22/policia-investiga-ataques-racistas-contra-mario-balotelli-tras-un-tuit-del-futbolista/"
        # link2 = 'http://cnnespanol.cnn.com/2015/01/06/una-familia-llora-la-perdida-de-siete-seres-queridos-en-el-vuelo-de-airasia/'
        # parser = CNNParser()
        related_news = self.service.get_list({}, 1)
        print 'len: ' + str(len(related_news))
        # self.assertTrue(len(related_news) == 1)
        #
        # self.assertIsNotNone(related_news)
        #
        # self.news_entry = parser.parse(link2)
        logger = get_logger('tecnonews')
        nes = NewsEntriesService()
        other_versions = []
        entry = nes.get_list({'title': 'Fiscalía pide el internamiento de cuatro menores detenidos en Lleida'})[0]
        entry.set_analisys_info()
        try:
            tsr = RelatedNewsEntries(entry)
            other_versions = tsr.get_other_versions_top_ten()
            entry.set_news_versions(other_versions)
            related = tsr.get_related_entities_top_5_not_in_list(other_versions)
            entry.set_related_news(related)
            logger.info("<Tecnonews> <_process> samenews diferente coverage number %s" % len(other_versions))
            logger.info("<Tecnonews> <_process> related_news number %s" % len(related))
        except Exception, e:
            logger.error("<Tecnonews> <_process> related_news %s" % entry.title)
            logger.error("<Tecnonews> <_process> related_news %s" % traceback.format_exc())
            logger.info(traceback.format_exc())

        sp = SimilarParagraph(entry, other_versions)
        content_with_insert = sp.get_content_after_insert()

        c = NewsRewriter(entry)

        c.rewritten_entry.content = content_with_insert

        # TODO: set c.rewritten_entry.content to the content of insert new
        logger.info('<Tecnonews> <_process> publishing note: ' + entry.source)
        try:
            # c.rewrite_title()
            c.rewrite_content()
            # c.publish()
            # entry.published_date = datetime.utcnow()
            # entry.wp_id = c.rewritten_entry.wp_id
            pass
        except Exception, e:
            logger.error("<Tecnonews> <_process> rewriting fail: %s " % (entry.title))
            logger.info(traceback.format_exc())

        # Always save
        logger.info("<<<")
        logger.info("entry : %s" % entry.title)
        logger.info("relateds: %s" % entry.related)

        # self.news_entry.set_related_news(related_news)
        # self.news_entry.set_news_versions(related_news)
        #
        # c = NewsRewriter(self.news_entry)
        # self.assertTrue(len(c.rewritten_entry.versions) > 0)
        # self.assertTrue(len(c.rewritten_entry.related) > 0)
        # #c.rewrite()
        # #be carefull to have a news entry on the collection properly before start
        #
        # c.publish()
        #
        # self.news_entry.wp_id = c.rewritten_entry.wp_id
        # # self.object_id = self.service.save(self.news_entry)
        # #
        # # unmarshalled_entry = self.service.get_list({'_id': self.object_id})[0]
        # self.assertIsNotNone(unmarshalled_entry)
        # self.assertEquals(unmarshalled_entry.wp_url[:12], "http://tecno")


if __name__ == '__main__':
    unittest.main()