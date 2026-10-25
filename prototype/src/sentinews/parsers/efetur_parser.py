#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class EfeturParser(GenericParser):
    def __init__(self):
        super(EfeturParser, self).__init__()

    source = "Efetur"

    def parse(self, url):
        #url = "http://www.efetur.com/noticia/yacimiento-por-descubrir/?utm_source=rss&utm_medium=rss&utm_campaign=yacimiento-por-descubrir"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()

        for caption in soup.findAll('p',{'class':'wp-caption-text'}):
            caption.extract()



        title = soup.find('h1')
        title =  title.text.strip()


        content = ""

        intro = soup.find('div',{'class':'entradilla'})
        if intro:
            content += intro.text.strip()# + "."


        paragraphs = soup.find('div',{'class':'post-entry'}).findAll(['p','h2'])


        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()


            content += "\n" + clean_text

            if paragraph.name == 'h2':
                content += "."


        content = content.strip()


        tags = ["turismo"]
        categories=["turismo"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
