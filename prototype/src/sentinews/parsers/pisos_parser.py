#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class PisosParser(GenericParser):
    def __init__(self):
        super(PisosParser, self).__init__()

    source = u"Pisos"
    
    def parse(self, url):
        #url = "http://www.pisos.com/noticias/noticias/mas-actualidad/barcelona-anuncia-un-paquete-de-2-000-viviendas-sociales/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+ActualidadPisosCom+%28Actualidad+Inmobiliaria%29&utm_content=FeedBurner"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        for sumario in soup.findAll('div',{'class':'sumario mobile-center '}):
            sumario.extract()
            
        for more in soup.findAll('p',{'class':'more'}):
            more.extract()
        
        title = soup.find('p',{'class':'title'})
        title =  title.text.strip()


        content = "" 
        
        intro = soup.find('div',{'class':'excerpt'})
        if intro:
            content = intro.text.strip()
        
        
        paragraphs = soup.find('div',{'class':'description'}).findAll('p')
        
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
