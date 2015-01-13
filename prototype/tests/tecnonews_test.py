# -*- coding: utf-8 -*-
from src.sentinews.blog_publisher import BlogPublisher
from src.sentinews.news_entry import NewsEntry
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_crawler.news_crawler import NewsCrawler
from src.utils.logger_utils import *
import traceback
import datetime
from src.sentinews.news_crawler.cnn_parser import CNNParser
import wikipedia as wk
from src.sentinews.news_crawler.cnn_crawler import CNNCrawler
import unittest
from src.services.mongodb.news_entries_service import NewsEntriesService
from bson.objectid import ObjectId

class TecnonewsTest(unittest.TestCase):
	''' Clase para testear una sola noticia end to end '''
	service = NewsEntriesService('test')
	news_entry = None
	object_id = None

	def test_end_2_end(self):
		link = "http://cnnespanol.cnn.com/2014/09/22/policia-investiga-ataques-racistas-contra-mario-balotelli-tras-un-tuit-del-futbolista/"
		link2 = 'http://cnnespanol.cnn.com/2015/01/06/una-familia-llora-la-perdida-de-siete-seres-queridos-en-el-vuelo-de-airasia/'
		parser = CNNParser()
		self.news_entry = parser.parse(link2)
		c = NewsRewriter(self.news_entry)
		#c.rewrite()
		#be carefull to have a news entry on the collection properly before start
		related_news = self.service.get_list({},1)
		self.assertIsNotNone(related_news)
		print 'len: ' + str(len(related_news))
		self.assertTrue(len(related_news) == 1)
		c.rewritten_entry.set_news_versions(related_news)
		c.rewritten_entry.set_related_news(related_news)
		c.publish()

		self.news_entry.set_related_news(related_news)
		self.news_entry.set_news_versions(related_news)
		self.news_entry.wp_id = c.rewritten_entry.wp_id
		self.object_id = self.service.save(self.news_entry)		
		
		unmarshalled_entry = self.service.get_list({'_id': self.object_id})[0]
		self.assertIsNotNone(unmarshalled_entry)
		self.assertEquals(unmarshalled_entry.wp_url[:12], "http://tecno")






if __name__ == '__main__':
	unittest.main()