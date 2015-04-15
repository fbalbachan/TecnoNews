from bs4 import BeautifulSoup
from urllib2 import urlopen
from src.sentinews.news_entry import NewsEntry
from src.sentinews.parsers.generic_parser import GenericParser


class BBCParser(GenericParser):
    def __init__(self):
        super(BBCParser, self).__init__()

    source = 'BBC'

    def parse(self, url, tags=None):
        content = None
        title = None
        soup = BeautifulSoup(urlopen(url))
        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        if soup is not None:
            article = soup.find('div', {'class': 'story-body'})
            if article is not None:
                title = article.find('h1', {'class': 'story-body__h1'}).text
                paragraphs = article.find('div', {'class': 'story-body__inner'}).find_all('p')
                content = ' '.join([paragraph.text + '\n' for paragraph in paragraphs])
                content = self.sanitize(content)

        news_parsed = None

        if len(content) > 1 and len(tags) > 0:
            news_parsed = NewsEntry(title, content, tags, self.source, url=url)

        return news_parsed