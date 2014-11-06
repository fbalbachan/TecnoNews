from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import *

class WallStreetParser(object):

	def parse(self, url, limit = 0):
		soup = BeautifulSoup(urlopen(url).open())
		top = soup.findAll('li', {"class": "firstList listFirst"})[0]