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


class ABCParser(GenericParser):
    def __init__(self):
        super(ABCParser, self).__init__()
        config = ConfigProvider()
        self.language_filter_status = config.get('language_filter', 'status')

    source = u"ABC"

    def parse(self, url):
        if u'/silencio-por-favor/' in url:
            return None

        soup = BeautifulSoup(self.opener(url).read(),
                             from_encoding='iso-8859-15')

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
        title = soup.find('h1', {"itemprop": "headline"})

        if not title:
            title = soup.find('span', {"itemprop": "headline"})

        title = title.text.strip()

        categories = [urlparse(url).path.split("/")[1]]

        # des = soup.find('article', {"class": "desarrollo"})
        # image_search_string = des.find('header').find('h2').text + u' '
        # image_search_string += title.split('.')[0]

        # No tags
        tags = set()

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
            logger.error(u"Couldn't parse news in elmundo ")
            logger.error(u"Url: %s " % url)

        return new_entry

