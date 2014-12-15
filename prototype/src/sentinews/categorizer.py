# -*- coding: utf-8 -*-
import ConfigParser
from src.utils.csvwrapper import unicode_csv_reader
from unidecode import unidecode
from sets import Set
import codecs
import warnings

class Categorizer(object):

	def __init__(self, tags):
		if len(tags) == 0:
			warnings.warn('Tags must not be empty!')
		
		self.tags = tags
		self.config = ConfigParser.ConfigParser()
		self.config.read('config')
		categories_file =  self.config.get("resources", "categories")
		countries_file = self.config.get("resources", "countries")
		categories_reader = unicode_csv_reader(open(categories_file, 'r'), first_line_is_header = False, delimiter=',')
		self.categories_dict = {}
		for row in categories_reader:
			self.categories_dict[row[0]] = [ element for element in row if element != '']
		countries_reader = unicode_csv_reader(open(countries_file, 'r'), first_line_is_header = False, delimiter=',')
		self.countries_list = [unidecode(country[0].lower()) for country in countries_reader]
		self.categories = self.__create_categories()


	def get_or_else(self):
		
		return self.categories if self.categories is not None else ['interés general']


	def __create_categories(self):
		categories = Set([])
		for element in self.tags:
			for category, list_tags in self.categories_dict.iteritems():
				for tag in list_tags:
					ltag = tag.lower()
					lelement = element.lower()
					if unidecode(lelement) in self.countries_list:
						categories.add('internacionales')
					if unidecode(lelement).find(unidecode(ltag)) > -1:
						categories.add(category)
		return categories
