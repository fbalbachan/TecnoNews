#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class CincoDiasParser(GenericParser):
    def __init__(self):
        super(CincoDiasParser, self).__init__()

    source = u"Cinco Dias"
    
    def parse(self, url):
        #url = "http://cincodias.com/cincodias/2015/12/17/sentidos/1450385127_093885.html#?ref=rss&format=simple&link=link"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
            
        for side in soup.findAll('div',{'class':'derecha'}):
            side.extract()
        
            
            
        title = soup.find('h1',{'id':'titulo_noticia'})
        title =  title.text.strip()
        
        
        content = "" 
            
        paragraphs = soup.find('div',{'id':'cuerpo_noticia'}).findAll('p')
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()

                
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
