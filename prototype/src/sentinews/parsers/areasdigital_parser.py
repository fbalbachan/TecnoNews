#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class AreasDigitalParser(GenericParser):
    def __init__(self):
        super(AreasDigitalParser, self).__init__()

    source = "Areas Digital"

    def parse(self, url):
        #url = "http://www.areas-digital.com.ar/nota.php?id=24554"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='windows-1252')
        for script in soup(["script", "style"]):
            script.extract()

        #-------------------TITLE--------------------------
        title = soup.find('h1')
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        intro = soup.find('h3')

        if intro is not None:
            content = intro.text.strip() + "\n"


        article_content = soup.find('div',{'class':'nota-texto'})

        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text


        categories = ["propiedades"]
        tags = ["propiedades"]

        #categories=[urlparse(url).path.split("/")[1]]
        #print categories

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
