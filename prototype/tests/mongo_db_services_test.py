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
		news = NewsEntry('Diego gana el prode', 'Reamente lo ganó', ['deportes','salud', 'delito'],
			'Euronews')

		self.assertIsNotNone(news)
		news_id = self.service.save(news)
		self.assertIsNotNone(news_id)
		print news_id


	def test_retrieve_single_news_entry_record(self):
		news = self.service.get_list({'title': 'Diego gana el prode'})
		self.assertIsNotNone(news)
		self.assertTrue(news.count() > 0)


	def test_retrieve_news_entry_list_by_given_date(self):
		oneday = timedelta(days=1)
		cursor = self.service.get_list({'published_date': {'$gte': datetime.utcnow() - oneday}})
		self.assertIsNotNone(cursor)
		self.assertTrue(cursor.count() > 0)
		print cursor.count()


	def test_retrieve_list_by_categories(self):
		cursor = self.service.get_list({'categories': {'$in': ['policiales']}})
		self.assertIsNotNone(cursor)
		self.assertTrue(cursor.count() > 0)
		print cursor.count()


if __name__ == '__main__':
	unittest.main()