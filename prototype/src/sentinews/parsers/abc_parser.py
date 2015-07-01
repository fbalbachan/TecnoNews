#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse
from src.sentinews.parsers.generic_parser import GenericParser


class ABCParser(GenericParser):
    def __init__(self):
        super(ABCParser, self).__init__()

    source = u"ABC"

    def parse(self, url):
        if u'/silencio-por-favor/' in url:
            return None

        soup = BeautifulSoup(self.opener.read(url),
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

        new_entry = self.create_news_entry(title, content, tags, self.source, url, categories,
                                           image_search_string)
        return new_entry

