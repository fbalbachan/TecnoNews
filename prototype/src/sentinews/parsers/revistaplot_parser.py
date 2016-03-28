#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class RevistaplotParser(GenericParser):
    def __init__(self):
        super(RevistaplotParser, self).__init__()

    source = u"revistaplot"
    
    def parse(self, url):
        #url = "http://www.revistaplot.com/es/finalistas-mchap-emerge-20142015/"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.select('#single-header h2')[0].text.strip()
        
        content = ""
        article_content = soup.select('#single-content')[0]
        
        paragraphs = article_content.findAll('p')

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
