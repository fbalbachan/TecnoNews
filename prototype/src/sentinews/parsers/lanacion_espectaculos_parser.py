#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback

from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import get_crawler_logger
from src.utils.configProvider import ConfigProvider
from src.sentinews.parsers.generic_parser import GenericParser
from urlparse import urlparse

logger = get_crawler_logger()


class LaNacionEspectaculosParser(GenericParser):
    def __init__(self):
        super(LaNacionEspectaculosParser, self).__init__()
        config = ConfigProvider()
        self.language_filter_status = config.get('language_filter', 'status')

    source = u"La Nacion espectaculos"

    def is_parseable_case(self, url, soup=None):
        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))


        tema_nota = soup.find('span', {"class": "tema-nota"})
        print "tema_nota %s" % tema_nota

        dislowed_keywords = [u'Bailando por un sueño',
                             u'Conversaciones',
                             u'LA NACION',
                             u'look']

        if tema_nota and any(k for k in dislowed_keywords if k in tema_nota):
            allowed = False

        return allowed

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url))

        if not self.is_parseable_case(url=url, soup=soup):
            return None

        image_search_string = None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove sharedaddy
        for social in soup.findAll('ul', {"class": "herramientas"}):
            social.extract()

        tweets = []

        for tweet in soup.findAll('div', {"class": "embed-twitter"}):
            tweets.append(tweet)
            tweet.extract()

        new_entry = None
        title = soup.find('h1', {"itemprop": "name headline"})

        title = title.text.strip()

        categories = None
        category = soup.find('span', {"itemprop": "title"}).text

        tags = [category]

        content = soup.find('section', {"itemprop": 'articleBody'}).text
        content = self.sanitize(content)
        manual_test_js = content.find('function()') == -1
        if not manual_test_js:
            logger.error("Has JS!! %s")
            return None

        if len(tags):
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
            logger.error(u"Couldn't parse news in elmundo ")
            logger.error(u"Url: %s " % url)

        return new_entry

