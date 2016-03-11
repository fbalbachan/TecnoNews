#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class FotoCasaParser(GenericParser):
    def __init__(self):
        super(FotoCasaParser, self).__init__()

    source = u"FotoCasa"
    
    def parse(self, url):
        #url = "http://www.fotocasa.es/blog/reformas/tienes-un-local-comercial-para-reformar-consejos-a-tener-en-cuenta"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
            
        for caption in soup.findAll('p',{'class':'wp-caption-text'}):
            caption.extract()
        
        soup.find('div',{'class':'post-footer'}).extract()
        
        title = soup.find('h3',{'class':'post-title'})
        title =  title.text.strip()


        content = "" 
        
        
        paragraphs = soup.find('div',{'class':'post-content'}).findAll('p')
        
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
