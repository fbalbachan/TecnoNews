#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re
from src.utils.unicodeTools import safe_unicode

class MarronyblancoParser(GenericParser):
    def __init__(self):
        super(MarronyblancoParser, self).__init__()

    source = u"marronyblanco"
    
    def parse(self, url):
        #url = "http://marronyblanco.com/entrevista-noelia-carrasco-directora-marketing-fersay/"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.select('h1.entry-title')[0].text.strip()
        
        content = ""
        article_content = soup.select('div.td-post-text-content')[0]
        
        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        
        categories = []
        tags = []

        tags        =   [u"electrodomésticos"]
        categories  =   [u"electrodomésticos"]
        title       =   safe_unicode(title)
        content     =   safe_unicode(content)
        
        #return {"title":title, "content":content}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
