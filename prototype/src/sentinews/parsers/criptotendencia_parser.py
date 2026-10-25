#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class CriptoTendenciaParser(GenericParser):
    source = "CriptoTendencia"

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url),
                             from_encoding='utf-8')

        title = soup.find('h1', {"class": 'entry-title'}).text.strip()
        pretags = soup.find('span', {"class": 'tags'}).findAll("a")
        tags = set(x.text.strip() for x in pretags)

        content = ""
        paragraphs = soup.find('div', {"class": 'entry-content'}).findAll('p')
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        content = content.strip()
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=["crypto"],
                                           image_search_string="",
                                           keywords=None)
        return new_entry
