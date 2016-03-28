#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class AmbitoFinancieroPlacerParser(GenericParser):
    def __init__(self):
        super(AmbitoFinancieroPlacerParser, self).__init__()

    source = u"Ambito Financiero - Placer"

    def parse(self, url):
        #url = "http://www.ambito.com/diario/noticia.asp?id=831750"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='windows-1252')
        for script in soup(["script", "style"]):
            script.extract()


        #for image in soup.findAll('img'):
        #    image.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('h2', {"id":"tituloDespliegue"})
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        intro = soup.find('span',{"id":"textoCopete"})

        if intro is not None:
            content = intro.text.strip() + "\n"


        article_content = soup.find('div',{"id": "textoDespliegue"})

        #paragraphs = article_content.findAll('p')

        for paragraph in article_content.stripped_strings:
            clean_text = paragraph
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
