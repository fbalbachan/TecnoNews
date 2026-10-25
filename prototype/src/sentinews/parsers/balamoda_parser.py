#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class BalamodaParser(GenericParser):
    def __init__(self):
        super(BalamodaParser, self).__init__()

    source = "Balamoda"
    
    def parse(self, url):
        #url = "http://www.balamoda.net/2016/01/currently-loving-las-cosas-que-me-ponen.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+balamoda+%28B+a+la+moda%29&utm_content=FeedBurner"
        
        soup = BeautifulSoup(self.opener.read(url), "html.parser", from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = ""
        for h in soup.select('h3[class*=post-title]'):
            title = h.text
        
        content = "" 
        
        paragraphs = soup.find("div",{"class","post-body"}).findAll("div")
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        if content == "" :
            content = article_content.text.strip()
        
        categories = []
        tags = []

        tags = ["belleza"]
        categories=["belleza"]
        #return {"content":content, "title":title}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
