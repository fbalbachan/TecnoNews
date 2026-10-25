import unittest
from src.sentinews.feeds import Feed
from src.services.mongodb.feeds_service import FeedService
from datetime import datetime

class FeedServiceTest(unittest.TestCase):

	def setUp(self):
		self.service = FeedService()


	def test_create_single_feed_object(self):
		feed = Feed('clarin', 'http://edant.clarin.com/shared/v7/rss/', datetime.utcnow())
		self.assertIsNotNone(feed)
		self.assertEqual(feed.id, 'clarin')

	def test_save_single_feed_object(self):
		feed = Feed('clarin', 'http://edant.clarin.com/shared/v7/rss/', datetime.utcnow())
		feed_id = self.service.save(feed)
		self.assertIsNotNone(feed_id)
		self.assertTrue(len(str(feed_id)) > 0) 

	def test_retrieve_list_feed_object(self):
		feed_list = self.service.get_all()
		self.assertIsNotNone(feed_list)
		self.assertTrue(len(feed_list) > 0)
		print(feed_list)


if __name__ == '__main__':
	unittest.main()

