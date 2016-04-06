#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re
from src.utils.unicodeTools import safe_unicode

class ElectroimagenParser(GenericParser):
    def __init__(self):
        super(ElectroimagenParser, self).__init__()

    source = u"electroimagen"
    
    def parse(self, url):
        #url = "http://electro-imagen.com/articulo/whirlpool-presenta-su-programa-fast-track-a-los-estudiantes-de-esade-en-la-feria-spring-fair"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.select('h1.title')[0].text.strip()
        
        content = ""
        article_content = soup.select('div.post-content')[0]
        
        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        

        tags        =   [u"electrodomésticos"]
        categories  =   [u"electrodomésticos"]
        title       =   safe_unicode(title)
        content     =   safe_unicode(content)
        
        tmptags = soup.select("p.post-terms")[0].findAll("a")
        for t in tmptags :
            tags.append( safe_unicode( t.text.strip() ) )
        
        
        #return {"title":title, "content":content, "tags" : tags}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
