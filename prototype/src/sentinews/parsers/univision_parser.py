__author__ = 'Pablo Perez De Angelis'
from bs4 import BeautifulSoup
from urllib2 import urlopen
from src.utils.logger_utils import get_crawler_logger
from src.sentinews.news_entry import NewsEntry


class UnivisionParser(object):

    def __init__(self):
        self.source = 'Univision'
        self.logger = get_crawler_logger()

    def parse(self, url, tags=None):
        """
        Parser of univision news site
        :param url: a univision news url
        :param tags: a list of default tags in case the site doesn't have tags
        :return: NewsEntry instance if the parser could parse or None in other case
        """
        content = None
        title = None
        parsed_news_entry = None

        soup = BeautifulSoup(urlopen(url))
        if soup is not None:
            title = soup.find('h1', {'class': 'article-header'})
            if not title:
                self.logger.error("\ncouldn't parse title from\n")
                self.logger.error("%s\n" % url)

            article = soup.find('div', {'class': 'article-text'})
            if not article:
                self.logger.error("\ncouldn't parse content from\n")
                self.logger.error("%s\n" % url)

            else:
                # remove video divs inside article
                for div in article.findAll('div', 'main-video-holder'):
                    div.extract()

                content = article

        # if we can parse the article then return an NewsEntry instance
        if content and title and len(tags) > 0:
            parsed_news_entry = NewsEntry(title.text,
                                          content.text,
                                          tags,
                                          self.source,
                                          url=url)

        return parsed_news_entry