#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class LugaresDeViajeParser(GenericParser):
    def __init__(self):
        super(LugaresDeViajeParser, self).__init__()

    source = "Lugares de Viaje"

    def parse(self, url):
        #url = "http://www.lugaresdeviaje.com/nota/pelourinho-a-vuelo-de-pajaro"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='windows-1252')
        for script in soup(["script", "style"]):
            script.extract()


        #for pics in soup.findAll('div', {'class': 'article_content_photo'}):
        #    pics.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('h1', {"class":"titulo"})
        title = title.text.strip()


        #-------------------CONTENT--------------------------
        content = ""

        intro = soup.find('div',{"class":"resumen"})

        if intro is not None:
            content = intro.text.strip() + "\n"

        article_content = soup.find('div',{"class": "contenido"})

        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        categories = ["turismo"]
        tags = ["turismo"]

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
