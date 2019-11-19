#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class CriptoNoticiasParse(GenericParser):
    source = u"CriptoNoticias"

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url),
                             from_encoding='utf-8')

        #title = soup.find('h1', {"class": 'jeg_post_title'}).text.strip()
        title = soup.find('div', {"class": 'data-title'}).text.strip()
        #pretags = soup.find('div', {"class": 'jeg_post_tags'}).findAll("a")
        #tags = set(x.text.strip() for x in pretags)

        content = ""
        #paragraphs = soup.find('div', {"class": 'content-inner'}).findAll('p')
        paragraphs = soup.find('div', {"class": 'resumen_item_text'}).findAll('p')
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        content = content.strip()

        #new_entry = self.create_news_entry(title=title, content=content,
        #                                   tags=tags,
        #                                   source=self.source,
        #                                   url=url,
        #                                   original_categories=["crypto"],
        #                                   image_search_string="",
        #                                   keywords=None)

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=["crypto"],
                                           source=self.source,
                                           url=url,
                                           original_categories=["crypto"],
                                           image_search_string="",
                                           keywords=None)


        return new_entry
