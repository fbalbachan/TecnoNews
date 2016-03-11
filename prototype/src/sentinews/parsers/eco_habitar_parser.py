#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class EcoHabitarParser(GenericParser):
    def __init__(self):
        super(EcoHabitarParser, self).__init__()

    source = u"EcoHabitar"
    
    def parse(self, url):
        #url = "http://www.ecohabitar.org/anpier-exige-a-rajoy-una-rectificacion/"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
            
            
        title = soup.find('h1',{'class':'entry-title'})
        title =  title.text.strip()
        
        content = "" 
        
        paragraphs = soup.find('div',{'class':'entry-content clearfix'}).findAll('p')
        
        
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
