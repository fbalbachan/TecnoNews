
# -*- coding: utf-8 -*-
import unittest
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.sentinews.news_entry import NewsEntry
from datetime import datetime, timedelta
from src.services.mongodb.connector import MongoConnector
from bson.objectid import ObjectId


class NewsEntryMongoServiceTest(unittest.TestCase):
	

	def setUp(self):
		self.service = NewsEntriesService('test')
		self.db = MongoConnector.get_instance('test')
		if self.db is not None:
			self.db.drop_collection('news_entries')
		self.news = NewsEntry(title=u'Diego ganó el prode', content=u'Reamente lo ganó. Aun laburando de ñoqui', 
			tags=['deportes','salud', 'delito'],source='Euronews',
			url="http://feed.clarin.com", wp_id='999',
			related=[ObjectId() for i in range(0,5)],
			versions=[ObjectId() for i in range(0,3)])
		self.news.published_date = datetime.utcnow()
		self.news_id = self.service.save(self.news)


	def test_check_service_creation(self):
		self.assertIsNotNone(self.service)

	def test_create_single_news_entry_record(self):
		self.assertIsNotNone(self.news_id)


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
		#"""there is an expected error regarding time difference btw creation and retrieve moment"""
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

	
	def test_retrieve_list_by_date_range(self):
		two_days = timedelta(days=2)
		start = datetime.utcnow() - two_days
		to = datetime.utcnow()
		new_list = self.service.get_by_date_range(start=start, to=to)
		self.assertIsNotNone(new_list)
		self.assertTrue(len(new_list) > 0)


	def test_retrieve_list_by_category(self):
		categories = ['deporte']
		new_list = self.service.get_by_categories(categories=categories)
		self.assertIsNotNone(new_list)
		self.assertTrue(len(new_list) > 0)


	def test_retrieve_list_by_categories(self):
		categories = ['deporte','salud']
		news_list = self.service.get_by_categories(categories=categories)
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) > 0)


	def test_retrieve_empty_list_by_category(self):
		categories = ['internacional']
		news_list = self.service.get_by_categories(categories=categories)
		self.assertIsNotNone(categories)
		self.assertTrue(len(news_list) == 0)


	def test_related_news(self):

		news_list = self.service.get_list({'_id': self.news_id})
		self.assertTrue(len(news_list[0].related) == 5)

	def test_retrieve_list_by_date_range_plus_category(self):
		categories= ['deporte']
		start = datetime.utcnow() - timedelta(days=2)
		to = datetime.utcnow()
		news_list = self.service.get_by_categories_date_range(start,to,categories)
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) == 1)

	def test_retrieve_list_with_object_id(self):
		news_list = self.service.get_list({'title': 'Diego ganó el prode'})
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) == 1)
		self.assertTrue(isinstance(news_list[0].object_id, ObjectId))
		for related_new_object_id in news_list[0].related:
			self.assertTrue(isinstance(related_new_object_id, ObjectId))

		self.assertEquals(len(news_list[0].versions), 3)
		for version_id in news_list[0].versions:
			self.assertTrue(isinstance(version_id, ObjectId))

		unmarshalled_news = self.service.get_list({'_id': news_list[0].object_id})
		self.assertIsNotNone(unmarshalled_news)
		self.assertTrue(len(unmarshalled_news) == 1)
		self.assertEquals(unmarshalled_news[0].title, self.news.title )


if __name__ == '__main__':
	unittest.main()