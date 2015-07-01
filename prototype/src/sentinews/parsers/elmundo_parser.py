#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser
from urlparse import urlparse


class ElMundoParser(GenericParser):
    def __init__(self):
        super(ElMundoParser, self).__init__()

    source = u"El Mundo"

    def parse(self, url):
        if u'/opinion/' in url:
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

        new_entry = self.create_news_entry(title, content, tags, self.source, url, categories,
                                           image_search_string)

        return new_entry

