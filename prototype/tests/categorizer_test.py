# -*- coding: utf-8 -*-
import unittest
import ConfigParser
from src.utils.csvwrapper import unicode_csv_reader

class CategorizerTest(unittest.TestCase):

	def setUp(self):
		self.config = ConfigParser.ConfigParser()
		self.config.read('config')
		categories_file =  self.config.get("resources", "categories")
		categories = unicode_csv_reader(open(categories_file, 'r'), first_line_is_header = False, delimiter=',')
		self.categories_dict = {}
		for row in categories:
			self.categories_dict[row[0]] = [ element for element in row[1:] if element != '']

	def test_read_categories_from_file(self):

		self.assertIsNotNone(self.categories_dict)
		self.assertTrue(len(self.categories_dict) > 0)


	def test_create_single_categoria(self):
		pass



if __name__ == '__main__':
	unittest.main()