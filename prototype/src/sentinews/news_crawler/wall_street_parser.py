from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import *

class WallStreetParser(object):

	def __init__(self):
		self._logger = get_logger('tecnonews')

	def parse(self, url, limit = 0):
		soup = BeautifulSoup(urlopen(url).read())
		top = soup.findAll('li', {"class": "listFirst"})[0]

		try:
			title = ''
		except Exception, e:
			self._logger('Title not found: [%s]' % top)
			self._logger('Error', e.strerror)

		content = self.__extract_content(top)
		tags = self.__extract_tags(top)
		return NewsEntry(title, content, tags, u'Wall Street Journal')


	def __extract_content(self, element):
		return ''


	def __extract_tags(self, element):
		return []