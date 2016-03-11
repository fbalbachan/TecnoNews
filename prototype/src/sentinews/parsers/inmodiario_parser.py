#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class InmodiarioParser(GenericParser):
    def __init__(self):
        super(InmodiarioParser, self).__init__()

    source = u"Inmodiario"
    
    def parse(self, url):
        #url = "http://www.inmodiario.com/170/22367/tendencias-inmobiliarias-necesidad-panorama-sector-inmobiliario.html"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
            
            
        title = soup.find('div',{'class':'detail-news titulo'})
        title =  title.text.strip()
        
        content = "" 
        
            
        paragraphs = soup.find('div',{'id':'contenedor-contenido'}).findAll(['p','ul'])

        
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
