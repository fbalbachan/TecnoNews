#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
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

        tags = list(tags)

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry

