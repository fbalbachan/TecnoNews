from bs4 import BeautifulSoup
from urllib2 import urlopen
from src.sentinews.news_entry import NewsEntry

class BBCParser(object):

	source = 'BBC'

	def parse(self, url, tags=None):
		content = ''
		print url
		soup = BeautifulSoup(urlopen(url))
		if soup is not None:
			article = soup.find('div', {'class': 'story-body'})
			if article is not None:
				title = article.find('h1', {'class': 'story-body__h1'}).text
				paragraphs = article.find('div', {'class': 'story-body__inner'}).find_all('p')
				content = ' '.join([paragraph.text + '\n' for paragraph in paragraphs])
			
		return NewsEntry(title, content, tags, self.source,
				url=url) if len(content) > 1 and len(tags) > 0 else None