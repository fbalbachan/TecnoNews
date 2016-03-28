#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class CaribbeanNewsDigitalParser(GenericParser):
    def __init__(self):
        super(CaribbeanNewsDigitalParser, self).__init__()

    source = u"Caribbean News Digital"

    def parse(self, url):
        #url = "http://www.caribbeannewsdigital.com/noticia/ryanair-denuncia-edreams-y-google"

	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()


        title = soup.find('h1',{'class':'title'})
        title =  title.text.strip()


        content = ""

        paragraphs = soup.find('div',{'id':'content-area'}).find('div',{'class':'content'}).findAll('p')


        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()


            content += "\n" + clean_text



        content = content.strip()


        tags = [u"interés general"]
        categories=[u"interés general"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
