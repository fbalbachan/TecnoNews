#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class DiarioDelViajeroParser(GenericParser):
    def __init__(self):
        super(DiarioDelViajeroParser, self).__init__()

    source = u"Diario del Viajero"
    
    def parse(self, url):
        #url = "http://www.diariodelviajero.com/espana/monasterio-de-silos-1?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+diariodelviajero+%28Diario+del+viajero%29"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
             
        title = soup.find('h1')
        title =  title.text.strip()
        
        content = "" 
        
        paragraphs = soup.find('div',{'class':'article-content'}).find('div',{'class':'blob'}).findAll('p')
        
        while paragraphs[-1].find('a') and "|" in paragraphs[-1].text:
            paragraphs.pop()
        
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
