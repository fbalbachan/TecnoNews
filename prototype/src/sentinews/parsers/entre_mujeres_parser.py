#!/usr/bin/python
# -*- coding: utf-8 -*-




from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class EntreMujeresParser(GenericParser):
    def __init__(self):
        super(EntreMujeresParser, self).__init__()

    source = "EntreMujeres"

    def parse(self, url):
        #url = "http://entremujeres.clarin.com/moda/look-de-celebrity/hijos-fashionistas-famosos-Instagram_0_1471053241.html"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()


        title = soup.find('h1', {'class':'titulo'})
        title = title.text.strip()

        subtitle = soup.find('h2', {'class':'bajada'})

        content = ""

        if subtitle:
            content = subtitle.text.strip() + "."


        paragraphs = soup.find('div',{'class':'nota'}).findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()

            if clean_text == "Seguí leyendo:":
                break
            if re.match('^[*]{2}.*[*]{2}$', clean_text) is not None:
                continue
            content += "\n" + clean_text

        content = content.strip()



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
