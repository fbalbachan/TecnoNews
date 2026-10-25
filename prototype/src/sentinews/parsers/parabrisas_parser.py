#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class ParabrisasParser(GenericParser):
    def __init__(self):
        super(ParabrisasParser, self).__init__()

    source = "Parabrisas"

    def parse(self, url):
        #url = "http://parabrisas.perfil.com/2016/04/01/subastan-fiat-500l-que-uso-el-papa-en-nueva-york/"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        #for pics in soup.findAll('div', {'class': 'article_content_photo'}):
        #    pics.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('div', {"id":"contenido"}).find('h1')
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        intro = soup.find('div',{"id":"descripcion"})

        if intro is not None:
            content = intro.text.strip() + "\n"

        article_content = soup.find('section',{"id": "content"})

        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        categories = ["automóviles"]
        tags = ["automóviles"]

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
