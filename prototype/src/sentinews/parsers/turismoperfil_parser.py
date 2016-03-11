#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class TurismoPerfilParser(GenericParser):
    def __init__(self):
        super(TurismoPerfilParser, self).__init__()

    source = u"TurismoPerfil"
    
    def parse(self, url):
        #url = "http://turismo.perfil.com/48891-de-viaje-por-el-desierto-de-los-mil-budas/"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.select('#contenido > .articulo h1')[0].text.strip()
        
        content = ""
        article_content = soup.select('#contenido .articulo')[0]
        
        paragraphs = article_content.select('p:not([class])')
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        
        categories = []
        tags = []

        tags = ["turismo"]
        categories=["turismo"]
        #return {"title":title, "content":content}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
