# -*- coding: utf-8 -*-
import unittest
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.sentinews.news_entry import NewsEntry
from datetime import datetime, timedelta
from src.services.mongodb.connector import MongoConnector


class NewsEntryMongoServiceTest(unittest.TestCase):
	

	def setUp(self):
		self.service = NewsEntriesService('test')
		self.db = MongoConnector.get_instance('test')
		if self.db is not None:
			self.db.drop_collection('news_entries')
		self.news = NewsEntry(title=u'Diego ganó el prode', content=u'Reamente lo ganó. Aun laburando de ñoqui', 
			tags=['deportes','salud', 'delito'],source='Euronews',
			url="http://feed.clarin.com")

		self.news_id = self.service.save(self.news)


	def test_check_service_creation(self):
		self.assertIsNotNone(self.service)

	def test_create_single_news_entry_record(self):
		self.assertIsNotNone(self.news_id)
		print self.news_id


	def test_retrieve_single_news_entry_record(self):
		news_list = self.service.get_list({'title': 'Diego ganó el prode'})
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) > 0)
		self.assertEquals(news_list[0].title, self.news.title)


	def test_retrieve_news_entry_list_by_given_date(self):
		oneday = timedelta(days=1)
		news_list = self.service.get_list({'published_date': {'$gte': datetime.utcnow() - oneday}})
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) > 0)
		

	def test_retrieve_news_by_given_date(self):
		"""there is an expected error regarding time difference btw creation and retrieve moment"""
		five_seconds = timedelta(seconds=5)
		news_list = self.service.get_list({'published_date': {'$gte': self.news.published_date - five_seconds}})
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) == 1)
		self.assertEquals(news_list[0].content, self.news.content)

	def test_retrieve_news_by_given_date_fail(self):
		five_seconds = timedelta(seconds=5)
		news_list = self.service.get_list({'published_date': {'$gte': self.news.published_date + five_seconds}})
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) == 0)

	def test_retrieve_list_by_categories(self):
		news_list = self.service.get_list({'categories': {'$in': ['policiales']}})
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) > 0)


if __name__ == '__main__':
	unittest.main()