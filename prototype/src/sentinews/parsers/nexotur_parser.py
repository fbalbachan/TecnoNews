#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class NexoturParser(GenericParser):
    def __init__(self):
        super(NexoturParser, self).__init__()

    source = u"Nexotur"
    
    def parse(self, url):
        #url = "http://www.nexotur.com/noticia/85491/Nexotur/El-Turismo-ese-gran-olvidado.html"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='windows-1252')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()

        for photo in soup.findAll('table',{'class':'foto'}):
            photo.extract()
        
        for quote in soup.findAll('blockquote'):
            quote.extract()
            
            
        title = soup.find('h1',{'class':'titulo'})
        title =  title.text.strip()
        
        content = "" 
        
        intro = soup.find('h3',{'class':'antesubtitulo'})
        if intro and not "|" in intro.text:
            content += intro.text.strip() + "."
            
        intro2 = soup.find('div',{'class':'entradilla'})
        if intro2:
            content += "\n" + intro2.text.strip()
        
        paragraphs = soup.find('div',{'class':'texto'})
        
        
        content += "\n" + re.sub(u'([^ ]+)[.]([A-Z][^ ]*)', r'\1.\n\2', paragraphs.text.strip()) #REEMPLAZA finparrafo.NuevoParrafo => finparrafo.\n NuevoParrafo

        
        content = content.strip()
        
        
        tags = []
        categories=[u"interés general"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
