#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from news_entry import NewsEntry
from src.sentinews.parsers.generic_parser import GenericParser


class ForbesMexicoParser(GenericParser):
    def __init__(self):
        super(ForbesMexicoParser, self).__init__()

    source = u"Forbes Mexico"

    def parse(self, url):
        
        soup = BeautifulSoup(self.opener.read(url))

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        image_search_string = None

        title = soup.find('h1', {"itemprop": "headline"})
        title = title.text.strip()

        metadata = soup.find('ul', {"class" : "meta"})
        category = metadata.find(href=re.compile('/category/'))
        categories = [category.text.strip()]

        tags = set()
        for tag in soup.findAll(rel='tag'):
            tags.add(tag.text.strip())

        content = soup.find('section', {"itemprop": 'articleBody'}).text
        content = self.sanitize(content)

        assert content.find('function()') == -1

        tags = list(tags)

        new_entry = NewsEntry(title=title, content=content,
                                    tags=tags,
                                    source=self.source,
                                    url=url,
                                    original_categories=categories,
                                    image_search_string=image_search_string)

        if not new_entry:
            print(u"Couldn't parse news in elmundo ")
            print(u"Url: %s " % url)

        return new_entry

