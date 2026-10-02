#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class VeinteMinutosViviendaParser(GenericParser):
    def __init__(self):
        super(VeinteMinutosViviendaParser, self).__init__()

    source = "20 Minutos Vivienda"

    def parse(self, url):
        #url = "http://www.20minutos.es/noticia/2635327/0/firma-hipotecas-vivienda/ralentiza-octubre-2015/sube-7-por-ciento/"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()

        for quote in soup.findAll('span',{'class':'quote_new'}):
            quote.extract()

        for facebook in soup.findAll('div',{'class':'fb-like-faces-wrapper'}):
            facebook.extract()



        title = soup.find('h1',{'class':'article-title'})
        title =  title.text.strip()

        content = ""

        paragraphs = soup.find('div',{'class':'article-content'}).findAll(['p','ul'])

        for paragraph in paragraphs:
            if paragraph.name == 'ul':
                clean_text = paragraph.text.strip()
            else:
                clean_text = re.sub('([^ ]+)[.]([A-Z][^A-Z ]*)', r'\1.\n\2', paragraph.text.strip())


            content += "\n" + clean_text


        content = content.strip()


        tags = ["propiedades"]
        categories=["propiedades"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
