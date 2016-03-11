#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class HolaParser(GenericParser):
    def __init__(self):
        super(HolaParser, self).__init__()

    source = u"Hola"
    
    def parse(self, url):
        #url = "http://www.hola.com/actualidad/2015112582300/sergio-alvarez-charlotte-murray-hola/"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.find('h1', {'itemprop':'headline'})
        title = re.sub(u' ?[^., ]{2,3}? ¡HOLA![,]?', '', title.text.strip()).strip()
        
        content = "" 
        
        paragraphs = soup.find('div',{'class':'body'}).findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()

            if re.match(u'^-', clean_text) is not None:
                continue
                
            content += "\n" + clean_text
        
        content = content.strip()
        
        categories = []
        raw_categories = soup.find('ol',{'class':'breadcrumb'})
        if raw_categories != None:
            raw_categories = raw_categories.findAll('a')
            for category in raw_categories:
                categories.append(category.text.strip())
        
        tags = []
        raw_tags = soup.find('section',{'class':'news-tags'})
        if raw_tags != None:
            raw_tags = raw_tags.findAll('a')
            for tag in raw_tags:
                tags.append(tag.text.strip())                


        #tags = ["estilo vida"]
        #categories=["estilo vida"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
