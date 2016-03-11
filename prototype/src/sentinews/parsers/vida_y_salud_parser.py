#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class VidaYSaludParser(GenericParser):
    def __init__(self):
        super(VidaYSaludParser, self).__init__()

    source = u"Vida y Salud"
    
    def parse(self, url):
        #url = "https://www.vidaysalud.com/diario/ejercicio/hay-muy-buenas-razones-para-hacer-ejercicios-con-pesas/?utm_source=rss&utm_medium=rss&utm_campaign=hay-muy-buenas-razones-para-hacer-ejercicios-con-pesas"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
            
        for linkparent in soup.findAll('a',{'id':'linkparentimg'}):
            linkparent.extract()
        
            
            
        title = soup.find('article',{'id':'single'}).find('h1')
        title =  title.text.strip()

        content = "" 

            
        paragraphs = soup.find('div',{'class':'entry blog_entry'}).findAll(['p','li'])

        
        for paragraph in paragraphs:
            clean_text = re.sub(u'^(.+©.+)|(Imagen:.+)$','',paragraph.text.strip())
            if paragraph.name == 'li':
                content += "\n-" +clean_text
            else:    
                content += "\n" + clean_text
            


        
        content = content.strip()
        
        
        tags = ["estilo vida"]
        categories=["estilo vida"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
