#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback

from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import get_crawler_logger
from src.utils.configProvider import ConfigProvider
from src.sentinews.parsers.generic_parser import GenericParser
from urlparse import urlparse

logger = get_crawler_logger()


class ElMundoParser(GenericParser):
    def __init__(self):
        super(ElMundoParser, self).__init__()
        config = ConfigProvider()
        self.language_filter_status = config.get('language_filter', 'status')

    source = u"El Mundo"

    def parse(self, url):
        soup = BeautifulSoup(urlopen(url).read())
        image_search_string = None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove sharedaddy
        for social in soup.findAll('ul', {"class": "redes-sociales"}):
            social.extract()
            
        tweets = []

        for tweet in soup.findAll('div', {"class": "embed-twitter"}):
            tweets.append(tweet)
            tweet.extract()

        new_entry = None
        title = soup.find('h1', {"itemprop": "headline"}).text
        categories = [urlparse(url).path.split("/")[1]]

        des = soup.find('article', {"class": "desarrollo"})
        image_search_string = des.find('header').find('h2').text + u' '
        image_search_string += title.split('.')[0]

        tags = set()

        tag_links = soup.findAll('section', {"class": "tags"})
        for tag in tag_links:
            links = tag.findAll('a')
            for l in links:
                if l.text.lower() != 'tags':
                    tags.add(l.text)


        content = soup.find('div', {"itemprop": 'articleBody'}).text
        content = self.sanitize(content)

        manual_test_js = content.find('function()') == -1
        if not manual_test_js:
            logger.error("Has JS!! %s")
            return None

        if (len(tags) or categories) and not u'video' in categories:
            tags = list(tags)
            try:
                new_entry = NewsEntry(title=title, content=content,
                                  tags=tags,
                                  source=self.source,
                                  url=url,
                                  original_categories=categories,
                                  image_search_string=image_search_string)

            except Exception as e:
                logger.error("%s" % e.message)
                logger.error(traceback.format_exc())

        if not new_entry:
            logger.error("Couldn't parse news in elmundo ")
            logger.error("Url: %s " % url)

        return new_entry

