#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser
from urlparse import urlparse


class ClarinExtrashowParser(GenericParser):
    def __init__(self):
        super(ClarinExtrashowParser, self).__init__()

    source = u"Clarin Extrashow"

    def is_parseable_case(self, url):
        allowed = True

        allowed_sections = [u'/cine/', u'/teatro/', u'/musica/']
        if not any(k for k in allowed_sections if k in url):
            allowed = False

        return allowed

    def parse(self, url):
        if not self.is_parseable_case(url):
            return None
        soup = BeautifulSoup(self.opener.read(url))

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

        title_div = soup.find('div', {"class": "int-nota-title"})
        title = title_div.find('h1')

        title = title.text.strip()

        categories = [urlparse(url).path.split("/")[2]]

        tags = set()
        tag_links = soup.findAll('section', {"class": "tags-bar"})
        for tag in tag_links:
            links = tag.findAll('a')
            for l in links:
                if l.text.lower() != 'tags':
                    tags.add(l.text)

        content = soup.find('div', {"class": 'nota'}).text

        new_entry = self.create_news_entry(title, content, tags, self.source, url, categories,
                                           image_search_string)

        return new_entry

