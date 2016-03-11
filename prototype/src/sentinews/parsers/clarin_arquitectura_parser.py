#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class ClarinArquitecturaParser(GenericParser):
    def __init__(self):
        super(ClarinArquitecturaParser, self).__init__()

    source = u"ClarinArquitectura"
    
    def parse(self, url):
        #url = "http://arq.clarin.com/construccion/propuesta-hacer-Nacional-Ley-Ascensores_0_1481252204.html"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.find('div',{'class':'bdArticle'}).find('h3')
        title =  title.text.strip()

        
        content = "" 
        
        intro = soup.find('div',{'class':'mb10'})
        if intro:
            content = intro.text.strip()


        paragraphs = soup.find('div',{'class':'bdArticle'}).find('div',{'class':'bd'}).findAll('p')
        
        for paragraph in paragraphs:
            clean_text = re.sub(u'^(Leer también|Leer más): .*$','', paragraph.text.strip()).strip()

                
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
