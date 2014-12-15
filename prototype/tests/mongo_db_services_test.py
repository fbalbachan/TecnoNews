# -*- coding: utf-8 -*-
import unittest
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.sentinews.news_entry import NewsEntry
from datetime import datetime, timedelta

class NewsEntryMongoServiceTest(unittest.TestCase):
	

	def setUp(self):
		self.service = NewsEntriesService()

	def test_check_service_creation(self):
		self.assertIsNotNone(self.service)

	def test_create_single_news_entry_record(self):
		news = NewsEntry(title='Diego gana el prode', content=u'Reamente lo ganó', 
			tags=['deportes','salud', 'delito'],source='Euronews',
			url="http://feed.clarin.com",
			title_lematized="", content_lematized="")

		self.assertIsNotNone(news)
		news_id = self.service.save(news)
		self.assertIsNotNone(news_id)
		print news_id


	def test_retrieve_single_news_entry_record(self):
		news_list = self.service.get_list({'title': 'Diego gana el prode'})
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) > 0)
		self.assertEquals(news_list[0].title, 'Diego gana el prode')


	def test_retrieve_news_entry_list_by_given_date(self):
		oneday = timedelta(days=1)
		news_list = self.service.get_list({'published_date': {'$gte': datetime.utcnow() - oneday}})
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) > 0)
		


	def test_retrieve_list_by_categories(self):
		news_list = self.service.get_list({'categories': {'$in': ['policiales']}})
		self.assertIsNotNone(news_list)
		self.assertTrue(len(news_list) > 0)


if __name__ == '__main__':
	unittest.main()