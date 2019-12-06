#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re


class DailyFxParser(GenericParser):
    source = u"DailyFx"

    def __init__(self):
        super(DailyFxParser, self).__init__()

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url))

        title = soup.find('h1', {"class": "dfx-articleHead__header"})
        title = title.text.strip()

        content = ""
        article_content = soup.find('p', {"class": "gsstx"}).findAll('span')
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
