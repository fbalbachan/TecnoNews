# -*- coding: utf-8 -*-
import unittest
from src.sentinews.news_entry import NewsEntry
from src.sentinews.publisher_host import WPHost
import ConfigParser
from src.utils.csvwrapper import unicode_csv_reader



class PublisherHostTest(unittest.TestCase):

	def setUp(self):
		self.host = WPHost('http://tecnonews.comule.com/xmlrpc.php', 'tecnonews', 'tecnonews1')
		self.config = ConfigParser.ConfigParser()
		self.config.read('config')


	def test_create_dict_from_file(self):
		user_per_categories = []
		self.assertIsNotNone(user_per_categories)
		self.assertFalse(len(user_per_categories) < 1)


	def test_create_entry_with_destination(self):
		newEntry = NewsEntry('Hoy llegue temprano', 'y me compre un cafe violento',
			['economía'], u'DiegoNews en español')
		self.assertIsNotNone(newEntry)
		self.assertEquals(newEntry.title, 'Hoy llegue temprano')
		self.assertIsNotNone(newEntry.categories)
		self.assertTrue(len(newEntry.categories) > 0)
		self.assertTrue(len(newEntry.destination[0]) > 0)


if __name__ == '__main__':
	unittest.main()