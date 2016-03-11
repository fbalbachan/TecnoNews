#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class TrendenciasbellezaParser(GenericParser):
    def __init__(self):
        super(TrendenciasbellezaParser, self).__init__()

    source = u"Trendenciasbelleza"
    
    def parse(self, url):
        #url = "http://belleza.trendencias.com/celebrities/si-te-las-cruzas-no-las-reconoces-celebrities-sin-maquillaje-gente-normal?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+trendenciasbelleza+%28Trendencias+Belleza%29"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.find('h1').text
        #title = re.sub(u' ?[^., ]{2,3}? ¡HOLA![,]?', '', title.text.strip()).strip()

        content = "" 
        
        paragraphs = soup.find('div',{'class':'article-content'}).findAll('p')
        del paragraphs[-2:] # The last 2 P tags are garbage.

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

