# -*- coding: utf-8 -*-
import unittest
import ConfigParser
from src.utils.csvwrapper import unicode_csv_reader
from src.sentinews.categorizer import *

class CategorizerTest(unittest.TestCase):

	def setUp(self):
		self.config = ConfigParser.ConfigParser()
		self.config.read('config')
		categories_file =  self.config.get("resources", "categories")
		categories = unicode_csv_reader(open(categories_file, 'r'), first_line_is_header = False, delimiter=',')
		self.countries = unicode_csv_reader(open(categories_file, 'r'), first_line_is_header = False, delimiter=',')
		self.categories_dict = {}
		for row in categories:
			self.categories_dict[row[0]] = [ element for element in row[1:] if element != '']

	def test_read_categories_from_file(self):

		self.assertIsNotNone(self.categories_dict)
		self.assertTrue(len(self.categories_dict) > 0)


	def test_raise_error_empty_tags(self):
		with self.assertRaises(ValueError) as cm:
			Categorizer([])

		self.assertEquals(cm.exception.message, 'Tags must not be empty!' )


	def test_create_single_category(self):
		tags = [u'Medicina',u'Empresa', u'Aplicación', u'Crimen', u'Salud']
		categories = Categorizer(tags).get_or_else()
		self.assertIsNotNone(categories)
		print categories
		self.assertTrue(len(categories) == 4)
		self.assertTrue(u'salud' in categories)
		self.assertTrue(u'economía' in categories)
		self.assertTrue(u'tecnología' in categories)


	def test_special_caracters(self):
		tags = [u'Afganistán']
		categories = Categorizer(tags).get_or_else()
		self.assertIsNotNone(categories)
		print categories
		self.assertTrue(len(categories) > 0)

if __name__ == '__main__':
	unittest.main()