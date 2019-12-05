#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class BloombergParser(GenericParser):
    source = u"Bloomberg"

    def parse(self, url):
        soup = BeautifulSoup(self.opener.read(url),
                             from_encoding='utf-8')

        title = soup.find('div', {'class':'headline-section'}). find('h1', {"class": 'h1-regular-7'}).text.strip()
        #pretags = soup.find('span', {"class": 'tags'}).findAll("a")
        tags = set() #set(x.text.strip() for x in pretags)

        content = ""
        paragraphs1 = soup.findAll('div', {"class": 'wpb_wrapper'})
        for paragraph in paragraphs1:
            for para in paragraph.find('div', {"class": 'wpb_wrapper'}).findAll('p')
                clean_text = para.text.strip()
                content += "\n" + clean_text
        content = content.strip()

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=["economia"],
                                           source=self.source,
                                           url=url,
                                           original_categories=["economia"],
                                           image_search_string="",
                                           keywords=None)
        return new_entry
