#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class GuapaalinstanteParser(GenericParser):
    def __init__(self):
        super(GuapaalinstanteParser, self).__init__()

    source = u"Guapaalinstante"
    
    def parse(self, url):
        #url = "http://www.guapaalinstante.com/2016/01/maquillaje-caducado.html"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        title = ""
        for h in soup.select('h1[class*=post-title]'):
            title = h.text
        
        content = "" 
        
        article_content = soup.find('div',{'itemprop':'articleBody'})
        
        #filters
        #1) Widget for rendering related posts.
        for div in article_content.select('div[id*=spark_static_widget]'):
            div.extract()
        
        paragraphs = article_content.findAll("p")
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        if content == "" :
            content = article_content.text.strip()

        #return content
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
