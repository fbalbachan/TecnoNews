from bs4 import BeautifulSoup
from urllib2 import urlopen
from src.sentinews.news_entry import NewsEntry
from src.utils.languageFilter import LanguageFilter
from ConfigParser import ConfigParser


class BBCParser(object):

	source = 'BBC'

	def __init__(self):
		self.language_filter = LanguageFilter()
		config = ConfigParser()
		config.read('config')
		self.language_filter_status = config.get('language_filter', 'status')

	def parse(self, url, tags=None):
		content = ''
		soup = BeautifulSoup(urlopen(url))
		if soup is not None:
			article = soup.find('div', {'class': 'story-body'})
			if article is not None:
				title = article.find('h1', {'class': 'story-body__h1'}).text
				paragraphs = article.find('div', {'class': 'story-body__inner'}).find_all('p')
				content = ' '.join([paragraph.text + '\n' for paragraph in paragraphs])

		if self.language_filter_status == 'ON' and len(content) > 0:
			content = self.language_filter.only_spanish_paragraph(content.encode("utf-8"))
		
		return NewsEntry(title, content, tags, self.source,
				url=url) if len(content) > 1 and len(tags) > 0 else None