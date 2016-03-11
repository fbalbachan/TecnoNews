#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class ElrincondemodaParser(GenericParser):
    def __init__(self):
        super(ElrincondemodaParser, self).__init__()

    source = u"Elrincondemoda"
    
    def parse(self, url):
        #url = "http://www.elrincondemoda.com/2016/01/tendencias-fitness-lo-que-nos-espera-en-2016/"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.find('h1', {"class" : "story-title"}).text
        
        content = "" 
        
        article_content = soup.find('div',{'id':'content-area'})
        
        paragraphs = article_content.findAll("p")
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        
        categories = []
        tags = []

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
