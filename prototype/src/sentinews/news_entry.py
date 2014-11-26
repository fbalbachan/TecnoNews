# -*- coding: utf-8 -*-
import ConfigParser
from src.sentinews.categorizer import Categorizer
from sets import Set
from src.sentinews.publisher_host import WPHost
from src.utils.csvwrapper import unicode_csv_reader
from unidecode import unidecode

'''Struct class to contain the news information'''


class NewsEntry(object):

	def __init__(self, title, content, tags, source):
		self.title = title
		self.content = content
		self.tags = tags
		self.source = source
		self.categories = None
		self.destination = None
		self.config = ConfigParser.ConfigParser()
		self.__setUp()

	def __setUp(self):
		self.config.read('config')
		user_per_categories_file = self.config.get(
		    'resources', 'user_per_categories')
		user_per_categories = unicode_csv_reader(open(user_per_categories_file, 'r'),
                                           first_line_is_header=False, delimiter=',')
		
		self.user_per_categories_dict = {}
		i = 0
		for row in user_per_categories:
			self.user_per_categories_dict[i] = {}
			self.user_per_categories_dict[i]['user'] = row[1]
			self.user_per_categories_dict[i]['host'] = row[0]
			self.user_per_categories_dict[i]['password'] = row[2]
			self.user_per_categories_dict[i]['categories'] = [
				element for element in row[3:] if element != '']
			i += 1

		self.categories = list(Categorizer(self.tags).get_or_else())
		self.destination = self.__get_hosts(self.categories)


	def __get_hosts(self,categories):
		hosts = Set([])
		for category in categories:
			for key in self.user_per_categories_dict:
				for user_category in self.user_per_categories_dict[key]['categories']:
					if unidecode(user_category.lower()) == unidecode(category.lower()):
						hosts.add(WPHost(self.user_per_categories_dict[key]['host'], 
							self.user_per_categories_dict[key]['user'],
							self.user_per_categories_dict[key]['password']))
		return hosts
