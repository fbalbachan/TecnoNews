#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class CNNParser(GenericParser):
    def __init__(self):
        super(CNNParser, self).__init__()

    source = u"CNN en español"

    def parse(self, url, limit=1):
        soup = BeautifulSoup(self.opener.read(url))

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

        image_search_string = None
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry

