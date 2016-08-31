#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class VogueParser(GenericParser):
    def __init__(self):
        super(VogueParser, self).__init__()

    source = u"Vogue"

    def parse(self, url):
        if u"/galerias/" in url:
            return None
        #url = "http://www.vogue.es/moda/news/articulos/nueva-serie-moda-creadores-gossip-girl-mila-kunis-juicy-couture/24478"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()


        title = soup.find('p', {"class" : "article_title"}).text

        content = ""

        article_content = soup.find('div',{'class':'article_content'})

        #filters
        #1) The journalist's name.
        #   It's the first EM tag in the content.
        article_content.find("em").extract()

        #2) A dash after the journalist's name.
        #   It's the first <SPAN class="dash"> tag in the content.
        article_content.find("span", {"class", "dash"}).extract()

        paragraphs = article_content.findAll("p")

        #3) The two last P tags are garbage.
        del paragraphs[-2:]

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        content = content.strip()

        categories = []
        tags = []

        tags = ["belleza"]
        categories=["belleza"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
