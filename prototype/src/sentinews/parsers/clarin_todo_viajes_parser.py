#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class ClarinTodoViajesParser(GenericParser):
    def __init__(self):
        super(ClarinTodoViajesParser, self).__init__()

    source = u"Clarin Todo Viajes"
    
    def parse(self, url):
        #url = "http://www.clarin.com/todoviajes/destinos/america-del-norte/razones-viajar-Vegas-ano_0_1502850046.html"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
            
        for volanta in soup.findAll('strong',{'class':'volanta'}):
            volanta.extract()
        
            
            
        title = soup.find('div',{'class':'int-nota-title'}).find('h1')
        title =  title.text.strip()
        
        
        content = "" 
        
        paragraphs = soup.find('div',{'class':'int-nota-title'}).findAll('p')
        
        if len(paragraphs) > 1:
            paragraphs.pop()
            
        paragraphs += soup.find('div',{'class':'nota'}).findAll('p')
        
        
        for paragraph in paragraphs:
            clean_text = re.sub(u'^(Leé también .+)|(FUENTE:.+)$','',paragraph.text.strip())
                
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
