#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from src.sentinews.parsers.generic_parser import GenericParser
import re

class IdBellezaParser(GenericParser):
    def __init__(self):
        super(IdBellezaParser, self).__init__()

    source = "Id Belleza"

    def parse(self, url):
        #url= "http://idbelleza.com/2016/01/13/iconos-de-la-belleza-diane-kruger/"

        soup = BeautifulSoup(self.opener.read(url),
                             from_encoding='utf-8')

        image_search_string = None


        for script in soup(["script", "style"]):
            script.extract()
        
        for caption in soup(['figcaption']):
            caption.extract()

        title = soup.find('h1', {"itemprop": "headline"})
        title = title.text.strip()        
        
        content = ""

        paragraphs = soup.find('div', {"itemprop": 'articleBody'}).findAll('p')
   
        for paragraph in paragraphs:
            clean_text = re.sub('^Imagen via:.+$', '', paragraph.text.strip())
            content += "\n" + clean_text
            
        #print content
        #exit()

        tags = ["belleza"]
        categories = ["belleza"]


        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry
