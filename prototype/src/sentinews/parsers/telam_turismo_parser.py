#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class TelamTurismoParser(GenericParser):
    def __init__(self):
        super(TelamTurismoParser, self).__init__()

    source = u"Telam - Turismo"

    def parse(self, url):
        #url = "http://www.telam.com.ar/notas/201603/140085-chaco-semana-santa-turismo.html"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='windows-1252')
        for script in soup(["script", "style"]):
            script.extract()


        #for image in soup.findAll('img'):
        #    image.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('div', {"class":"title"}).find('h2')
        title = title.text.strip()


        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('p',{"class":"intro"})

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find('div',{"class": "editable-content"})

        paragraphs = article_content

        for paragraph in paragraphs.stripped_strings:
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
