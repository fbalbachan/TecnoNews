#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class CordobaTurismoParser(GenericParser):
    def __init__(self):
        super(CordobaTurismoParser, self).__init__()

    source = "Cordoba Turismo"

    def parse(self, url):
        #url = "http://www.cordobaturismo.gov.ar/el-valle-de-traslasierra-y-la-semana-brocheriana/"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()

        for linkparent in soup.findAll('a',{'id':'linkparentimg'}):
            linkparent.extract()

        title = soup.find('div',{'id':'single_titulo'})
        title =  title.text.strip()


        #print title
        #exit()
        content = ""



        paragraphs = soup.find('div',{'class':'entry-content'}).findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()


            content += "\n" + clean_text


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
