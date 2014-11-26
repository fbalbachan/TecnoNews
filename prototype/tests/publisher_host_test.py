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
		user_per_categories_file = self.config.get('resources','user_per_categories')
		user_per_categories = unicode_csv_reader(open(user_per_categories_file, 'r'),
			first_line_is_header=False, delimiter=',')
		self.user_per_categories_dict = {}
		i = 0
		for row in user_per_categories:
			self.user_per_categories_dict[i] = {}
			self.user_per_categories_dict[i]['host'] = row[0]
			self.user_per_categories_dict[i]['user'] = row[1]
			self.user_per_categories_dict[i]['password'] = row[2]
			self.user_per_categories_dict[i]['categories'] = [element for element in row[3:] if element != '']
			i = i + 1


	def test_user_per_categories(self):
		self.assertIsNotNone(self.user_per_categories_dict)
		self.assertTrue(len(self.user_per_categories_dict) > 0)


	def test_create_entry_with_destination(self):
		newEntry = NewsEntry('Hoy llegue temprano', 'y me compre un cafe violento',
			['economía', 'salud'], u'DiegoNews en español')
		self.assertIsNotNone(newEntry)
		self.assertEquals(newEntry.title, 'Hoy llegue temprano')
		self.assertIsNotNone(newEntry.categories)
		self.assertTrue(len(newEntry.categories) > 0)
		self.assertTrue(len(newEntry.destination) > 0)
		for host in newEntry.destination:
			print host.user


if __name__ == '__main__':
	unittest.main()