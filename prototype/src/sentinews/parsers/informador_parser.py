#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup
from urlparse import urlparse
from src.sentinews.parsers.generic_parser import GenericParser


class InformadorParser(GenericParser):
    def __init__(self):
        super(InformadorParser, self).__init__()

    source = u"Informador"

    def is_parseable(self, url, soup=None):
        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))

        return allowed

    def parse(self, url):
        html_string = self.opener.read(url)
        html_string_with_newlines = re.sub(r'<br>(&nbsp;)?<br>', '\n', html_string)
        soup = BeautifulSoup(html_string_with_newlines)

        if not self.is_parseable(url=url, soup=soup):
            return None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        image_search_string = None

        title = soup.find('div', {"class": "tituloInt"})
        title = title.h1.text

        categories = [urlparse(url).path.split("/")[1]]

        content = soup.find('div', {"id": "wpr-txt"})

        # Remove place and date
        place_date = content.find('strong')
        place_date.extract()

        tag_list = soup.find('div', {"id": "temasNoticia"})
        tags = []
        for tag in tag_list.findAll('a'):
            tags.append(tag.text)

        content = content.text
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry
