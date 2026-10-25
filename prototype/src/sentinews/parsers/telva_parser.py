#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re


class TelvaParser(GenericParser):
    def __init__(self):
        super(TelvaParser, self).__init__()

    source = "Telva"

    def parse(self, url):
        # url = "http://www.telva.com/2016/01/13/belleza/1452686897.html"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='iso-8859-15')
        for script in soup(["script", "style"]):
            script.extract()

        for image in soup.findAll('img'):
            image.extract()

        title = soup.find('h1', {"itemprop": "headline"}).text

        content = ""

        article_content = soup.find('section', {'itemprop': 'articleBody'})

        # filters
        # 1) Tags FIGURE inside the post body.
        for div in article_content.select('figure'):
            div.extract()

        # 2) There are H2 tags with meaningful data but outside P tags.
        #   We put those inside a P in order to normalize that data.
        for h2 in article_content.select('h2'):
            p = soup.new_tag("p")
            h = soup.new_tag("h2")
            h.string = h2.text
            p.append(h)
            h2.replace_with(p)

        paragraphs = article_content.findAll("p")

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        content = content.strip()
        if content == "":
            content = article_content.text.strip()

        categories = []
        tags = []

        tags = ["belleza"]
        categories = ["belleza"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
