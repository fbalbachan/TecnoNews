#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class AfuegolentoParser(GenericParser):
    def __init__(self):
        super(AfuegolentoParser, self).__init__()

    source = "Afuegolento"
    
    def parse(self, url):
        #url = "http://www.afuegolento.com/noticias/cocina/noticia/17551/vinos/alicante/dop/realizaran/salon/profesional/dar/conocer/sus/novedades"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        title = soup.find('div', {"class","descTitular"}).text.strip()
        content = "" 
        #article_content = soup.find('div',{'class':'detallesNoticia'})
        article_content = soup.find('div',{'style':'font-size:16px;line-height:22px;'})
        
        #paragraphs = article_content.findAll("div")
        
        #for paragraph in paragraphs:
        #    clean_text = paragraph.text.strip()
        #    content += "\n" + clean_text
        
        #content = content.strip()
        content = article_content.text.strip()
        if content == "" :
            content = article_content.text.strip()

        #return {"title" : title, "content" : content}
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
