import unittest
from src.services.mongodb.news_entries_service import NewsEntriesService
from src.sentinews.news_entry import NewsEntry

class NewsEntryMongoServiceTest(unittest.TestCase):
	

	def setUp(self):
		self.service = NewsEntriesService()

	def test_check_service_creation(self):
		self.assertIsNotNone(self.service)

	def test_create_service_single_service_model(self):
		news = NewsEntry('Diego gana el prode', 'Reamente lo ganó', ['deportes'],
			'Euronews')

		self.assertIsNotNone(news)
		news_id = self.service.save(news)
		self.assertIsNotNone(news_id)
		print news_id


	def test_create_single_news_entry_record(self):
		news = self.service.get_list({'title': 'Diego gana el prode'})
		self.assertIsNotNone(news)
		self.assertTrue(news.count() > 0)


	def test_retrieve_single_news_entry_record(self):
		pass


	def test_retrieve_news_entry_list_by_given_date(self):
		pass


if __name__ == '__main__':
	unittest.main()