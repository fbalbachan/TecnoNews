# -*- coding: utf-8 -*-
import unittest
from src.utils.configProvider import ConfigProvider
from src.sentinews.categorizer import *


class CategorizerTest(unittest.TestCase):
    def setUp(self):
        self.config = ConfigProvider()
        categories_file = self.config.get("resources", "categories")
        categories = unicode_csv_reader(open(categories_file, 'r', encoding="utf-8"), first_line_is_header=False, delimiter=',')
        self.countries = unicode_csv_reader(open(categories_file, 'r', encoding="utf-8"), first_line_is_header=False, delimiter=',')
        self.categories_dict = {}
        for row in categories:
            self.categories_dict[row[0]] = [element for element in row[1:] if element != '']

    def test_read_categories_from_file(self):
        self.assertIsNotNone(self.categories_dict)
        self.assertTrue(len(self.categories_dict) > 0)


    def test_raise_error_empty_tags(self):
        with self.assertRaises(ValueError) as cm:
            Categorizer([])

        self.assertEqual(str(cm.exception), 'Tags must not be empty!')


    def test_create_single_category(self):
        tags = ['Medicina', 'Empresa', 'Aplicación', 'Crimen', 'Salud']
        categories = Categorizer(tags).get_or_else()
        self.assertIsNotNone(categories)
        self.assertTrue(len(categories) == 4)
        print('categories')
        print(categories)
        self.assertTrue('salud' in categories)
        self.assertTrue('economía' in categories)
        self.assertTrue('tecnología' in categories)


    def test_special_caracters(self):
        tags = ['Afganistán']
        categories = Categorizer(tags).get_or_else()
        self.assertIsNotNone(categories)
        self.assertTrue(len(categories) > 0)

    def test_not_defined_category(self):
        tags = ['religión']
        categories = Categorizer(tags).get_or_else()
        self.assertIsNotNone(categories)
        print(categories)
        self.assertTrue(len(categories) == 1)
        self.assertEqual(categories[0] == 'interés general')


if __name__ == '__main__':
    unittest.main()