#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class DirectoalpaladarParser(GenericParser):
    def __init__(self):
        super(DirectoalpaladarParser, self).__init__()

    source = u"Directoalpaladar"
    
    def parse(self, url):
        #url = "http://www.directoalpaladar.com/otros/te-apetece-un-adorable-personaje-de-disney-para-desayunar?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+directoalpaladar+%28Directo+al+paladar%29"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        title = soup.find("h1", {"class", "article-header"}).text.strip()
        
        content = "" 
        article_content = soup.find("div", {"class", "article-summary"})
        
        paragraphs = article_content.findAll("p")[:-1]
        
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
