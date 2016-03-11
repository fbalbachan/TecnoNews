#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class DiariodegastronomiaParser(GenericParser):
    def __init__(self):
        super(DiariodegastronomiaParser, self).__init__()

    source = u"Diariodegastronomia"
    
    def parse(self, url):
        #url = "http://diariodegastronomia.com/los-ocho-mejores-virgen-extra-de-jaen/"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        title = ""
        for h in soup.select('h1[class*=post-title]'):
            title = h.text.strip()
        
        content = "" 
        article_content = []
        
        tmp = soup.select('div.post-content')
        for div in tmp:
            article_content = div
        
        paragraphs = article_content.findAll("p")
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        
        if content == "" :
            content = article_content.text.strip()

        #return {"title" : title, "content" : content}
        categories = []
        tags = []

        tags = [u"gastronomía"]
        categories=["estilo vida"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
