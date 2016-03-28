#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class SantiagodemolinaParser(GenericParser):
    def __init__(self):
        super(SantiagodemolinaParser, self).__init__()

    source = u"santiagodemolina"
    
    def parse(self, url):
        #url = "http://www.santiagodemolina.com/2016/03/levantar-un-muro.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Multiples+%28multiples%29&utm_content=FeedBurner"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.select('h3.post-title')[0].text.strip()
        
        content = ""
        article_content = soup.select('div.post-body')[0]
        
        paragraphs = article_content.findAll('div')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        
        categories = []
        tags = []

        tags = ["propiedades"]
        categories=["propiedades"]
        #return {"title":title, "content":content}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
