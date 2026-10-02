#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re


class ABC_Economia_Parser(GenericParser):
    source = "ABC Economia"

    def __init__(self):
        super(ABC_Economia_Parser, self).__init__()

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url))

        title = soup.find('span', {"class": "titular"})
        title = title.text.strip()

        content = ""
        article_content = soup.find('span', {"class": "cuerpo-texto"}).findAll('p')
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
