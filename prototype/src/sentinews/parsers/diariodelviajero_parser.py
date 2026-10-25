#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class DiariodelviajeroParser(GenericParser):
    def __init__(self):
        super(DiariodelviajeroParser, self).__init__()

    source = "Diariodelviajero"
    
    def parse(self, url):
        #url = "http://www.diariodelviajero.com/gastronomia/turismo-gastronomico-comer-cocido-en-una-finca-rustica-de-toledo"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        title = soup.find('h1').text
        content = "" 
        article_content = []
        
        article_content = soup.find("div", {"class" : 'article-content'}).find("div", {"class" : "blob"})
        #for div in tmp:
        #    article_content = div
        
        paragraphs = article_content.findAll("p")[:-1]

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        
        if content == "" :
            content = article_content.text.strip()

        #return {"content":content, "title" : title}
        categories = []
        tags = []

        tags = ["estilo vida"]
        categories=["estilo vida"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
