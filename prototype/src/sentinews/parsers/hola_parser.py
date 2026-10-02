#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class HolaParser(GenericParser):
    def __init__(self):
        super(HolaParser, self).__init__()

    source = "Hola"
    
    def parse(self, url):
        #url = "http://www.hola.com/actualidad/2015112582300/sergio-alvarez-charlotte-murray-hola/"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.find('h1', {'itemprop':'headline'})
        title = re.sub(' ?[^., ]{2,3}? ¡HOLA![,]?', '', title.text.strip()).strip()
        
        content = ""
        
        paragraphs = soup.find('div',{'class':'body'})
        if paragraphs is None:
            paragraphs = soup.find(True, {'itemprop':'articleBody'})
          
        paragraphs = paragraphs.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            for a_tag in paragraph.findAll(["strong", "a"]):
                a_tag.extract()
            no_tag_text = paragraph.text.strip()
            #print clean_text
            #print no_tag_text

            if re.match('^-', clean_text) is not None:
                continue
                
            if no_tag_text != "":
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


        tags = ["belleza"]
        categories=["belleza"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
