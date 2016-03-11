#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser

class MujerHoyParser(GenericParser):
    def __init__(self):
        super(MujerHoyParser, self).__init__()

    source = u"MujerHoy"
    
    def parse(self, url):
        #url = "http://www.mujerhoy.com/moda/moda-vip/looks-famosas-rosa-cuarzo-pantone-2016-920125112015.html"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.find('h1', {'class':'headline regular entry-title'})
        title =  title.text.strip()
        
        content = "" 
        
        intro = soup.find('ul', {'class':'descripcion-temas-pagina-final'})
        if intro:
            content = intro.text.strip()
        
        

        
        paragraphs = soup.find('div',{'class':'entry content'}).findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()

                
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
