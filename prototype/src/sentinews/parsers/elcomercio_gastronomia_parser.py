#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class ElcomercioGastronomiaParser(GenericParser):
    def __init__(self):
        super(ElcomercioGastronomiaParser, self).__init__()

    source = "ElcomercioGastronomia"
    
    def parse(self, url):
        #url = "http://elcomercio.pe/gastronomia/recetas/facebook-aprende-hacer-panqueques-saludables-solo-dos-ingredientes-video-noticia-1872084"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()

        #for iframe in soup.findAll('iframe'):
        #    iframe.extract()

        title = soup.find("h1").text.strip()
        
        content = "" 
        article_content = None
        tmp = soup.select("div[itemprop=articleBody]")
        for div in tmp:
            article_content = div
        
        paragraphs = article_content.findAll("p")
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        
        if content == "" :
            content = article_content.text.strip()

        #return {"title" : title , "content" : content}
        categories = []
        tags = []

        tags = ["gastronomía"]
        categories=["estilo vida"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
