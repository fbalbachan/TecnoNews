#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re


class FinanzasParser(GenericParser):
    source = u"Finanzas"

    def __init__(self):
        super(FinanzasParser, self).__init__()

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url))

        title = soup.find('h1', {"itemprop": "headline"})
        title = title.text.strip()

        content = ""
        article_content = soup.find('div', {"class": "contenido_noticia"}).findAll('p')
        for paragraph in article_content:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=["economia"],
                                           source=self.source,
                                           url=url,
                                           original_categories=["economia"],
                                           image_search_string=None,
                                           keywords=None)
        return new_entry
