#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class Pagina12TurismoParser(GenericParser):
    def __init__(self):
        super(Pagina12TurismoParser, self).__init__()

    source = u"Pagina 12 - Turismo"

    def parse(self, url):
        #url = "http://www.pagina12.com.ar/diario/suplementos/turismo/9-3314-2016-03-20.html"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='windows-1252')
        for script in soup(["script", "style"]):
            script.extract()


        #for image in soup.findAll('img'):
        #    image.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('div', {"class":"nota"}).find('h2')
        title = title.text.strip()


        #-------------------CONTENT--------------------------
        content = ""

        intro = soup.find('p',{"class":"intro"})

        if intro is not None:
            content = intro.text.strip() + "\n"


        article_content = soup.find('div',{"id": "cuerpo"})

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
