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
		for row in user_per_categories:
			self.user_per_categories_dict[row[1]] = {}
			self.user_per_categories_dict[row[1]]['host'] = row[0]
			self.user_per_categories_dict[row[1]]['password'] = row[2]
			self.user_per_categories_dict[row[1]]['categories'] = [
				element for element in row[3:] if element != '']

		self.categories = list(Categorizer(self.tags).get_or_else())
		self.destination = self.__get_hosts(self.categories)


	def __get_hosts(self,categories):
		hosts = Set([])
		for category in categories:
			for user in self.user_per_categories_dict:
				for user_category in self.user_per_categories_dict[user]['categories']:
					if unidecode(user_category.lower()) == unidecode(category.lower()):
						hosts.add(WPHost(self.user_per_categories_dict[user]['host'], 
							user, self.user_per_categories_dict[user]['password']))
		return hosts
