#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback

from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup
from src.utils.logger_utils import get_crawler_logger
from src.utils.configProvider import ConfigProvider
from src.sentinews.parsers.generic_parser import GenericParser

logger = get_crawler_logger()


class CNNParser(GenericParser):
    def __init__(self):
        super(CNNParser, self).__init__()
        config = ConfigProvider()
        self.language_filter_status = config.get('language_filter', 'status')

    source = u"CNN en español"

    def parse(self, url, limit=1):
        soup = BeautifulSoup(self.opener(url).read())

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Remove sharedaddy
        for sharedaddy in soup.findAll('div', {"class": "sharedaddy"}):
            sharedaddy.extract()
            
        tweets = []

        for tweet in soup.findAll('div', {"class": "embed-twitter"}):
            tweets.append(tweet)
            tweet.extract()

        new_entry = None
        title = soup.find('h1', {"class": "headline-article-main"}).text
        content = soup.find('div', {"class": "content-body-text"}).text
        content = self.sanitize(content)
        categories = [soup.find('div', {"class": "cat-section"}).text.strip()]
        categories = [x for x in categories if not 'CNN' in x]

        tags = set()

        tag_links = soup.findAll('div', {"class": "tags"})
        for tag in tag_links:
            links = tag.findAll('a')
            for l in links:
                if not 'CNN' in l.text:  #avoid CNN tags
                    tags.add(l.text)

        manual_test_js = content.find('function()') == -1
        if not manual_test_js:
            logger.error("Has JS!! %s")
            return None

        if len(tags) and not u'video' in categories:
            tags = list(tags)
            try:
                new_entry = NewsEntry(title=title, content=content,
                                  tags=tags,
                                  source=self.source,
                                  url=url,
                                  original_categories=categories)

            except Exception as e:
                logger.error("%s" % e.message)
                logger.error(traceback.format_exc())

        if not new_entry:
            logger.error("Couldn't parse news in CNN ")
            logger.error("Url: %s " % url)

        return new_entry

