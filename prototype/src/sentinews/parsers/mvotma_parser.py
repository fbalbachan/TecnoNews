#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re


class MvotmaParser(GenericParser):
    def __init__(self):
        super(MvotmaParser, self).__init__()

    source = "Mvotma"
    
    def parse(self, url):
        #url = "http://www.mvotma.gub.uy/sala-de-prensa/noticias/item/10007447-documento-de-aptitud-tecnica-informacion-a-tener-en-cuenta.html"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
                
        title = soup.find('h2',{'class':'itemTitle'})
        title =  title.text.strip()


        content = "" 
        
        
        paragraphs = soup.find('div',{'class':'itemFullText'}).findAll('p')
        
        
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
