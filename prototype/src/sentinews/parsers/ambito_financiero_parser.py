#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re


class AmbitoFinancieroParser(GenericParser):
    source = u"Ambito Financiero"

    def __init__(self):
        super(AmbitoFinancieroParser, self).__init__()

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url))

        title = soup.find('h1', {"class": "entry-title"})
        title = title.text.strip()

        content = ""
        article_content = soup.find('div', {"class": "td-post-content"}).findAll('p'):
        for paragraph in article_content:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        categories = ["economia"]
        tags = ["economia"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
