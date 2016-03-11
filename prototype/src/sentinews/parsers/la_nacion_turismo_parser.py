#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class LaNacionTurismoParser(GenericParser):
    def __init__(self):
        super(LaNacionTurismoParser, self).__init__()

    source = u"La Nación Turismo"
    
    def parse(self, url):
        #url = "http://www.lanacion.com.ar/1855159-quito-una-capital-a-la-altura"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()

        for aside in soup.findAll('aside',{'class':'mas-sobre-tema'}):
            aside.extract()
        
            
            
        title = soup.find('h1',{'itemprop':'headline'})
        title =  title.text.strip()
        
        
        content = "" 
        
        intro = soup.find('p',{'class':'bajada'})
        if intro:
            content += intro.text.strip() + "."
            
            
        paragraphs = soup.find('section',{'id':'cuerpo'}).findAll(['p','h2'])
        
        
        for paragraph in paragraphs:
            clean_text = re.sub(u'[ ]{2,}', ' ', paragraph.text.strip())

                
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
