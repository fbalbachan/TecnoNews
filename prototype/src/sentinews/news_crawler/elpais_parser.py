from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import *

class ElPaisParser(object):

	source = u'El Pais'
	
	def parse(self, url, limit = 1):
		soup = BeautifulSoup(urlopen(url).read())
		articles = soup.find_all('div', {'class': 'article estirar'}, limit = limit)
		new_entries = []
		if articles is not None:
			for article in articles:
				title = article.find('h2').find('a').text
				article_url = article.find('h2').find('a')['href']
				content = self.__extract_content(article_url)
				tags = []
				new_entries.append(NewsEntry(title, content, tags, self.source))
		return new_entries


	def __extract_content(self, article_url):
		soup = BeautifulSoup(urlopen(article_url).read())
		content = ''
		if soup is not None:
			content = str(soup.find('div',{'id': 'cuerpo_noticia'}).find_all(
				'p'))
		return content