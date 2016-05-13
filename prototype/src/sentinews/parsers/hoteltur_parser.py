#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class HotelturParser(GenericParser):
    def __init__(self):
        super(HotelturParser, self).__init__()

    source = u"Hosteltur"

    def parse(self, url):
        #url = "http://www.hosteltur.com.uy/117420_dgi-uruguay-cambia-criterio-inspecciones-comercios-verano.html"

	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()


        title = soup.find('h1',{'class':'titulo'})
        title =  title.text.strip()


        content = ""

        intro = soup.find('h3',{'class':'subtitulo'})
        if intro:
            content += intro.text.strip() + "."

        intro2 = soup.find('section',{'class':'content'}).find('div',{'class':'entradilla'})
        if intro2:
            content += "\n" + intro2.text.strip()


        paragraphs = soup.find('section',{'class':'content'}).find('div',{'class':'entrada'}).findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()


            content += "\n" + clean_text


        content = content.strip()

        tags = [u"turismo"]
        categories=[u"turismo"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
