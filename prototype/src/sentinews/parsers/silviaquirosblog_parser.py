#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class SilviaquirosblogParser(GenericParser):
    def __init__(self):
        super(SilviaquirosblogParser, self).__init__()

    source = "Silviaquirosblog"
    
    def parse(self, url):
        #url = "http://silviaquirosblog.com/2016/01/exfoliante-facial-purify-4d-de-sepai.html"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.find('h1', {"class" : "entry-title"}).text
        
        content = "" 
        
        article_content = soup.find('div',{'class':'entry-content'})
        
        #filters
        #1) Image caption texts.
        for div in article_content.select('div[class*=wp-caption]'):
            div.extract()
        
        paragraphs = article_content.findAll("p")
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        
        categories = []
        tags = []

        tags = ["belleza"]
        categories=["belleza"]
        #return content
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
