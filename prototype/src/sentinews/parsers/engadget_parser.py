#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class EngadgetParser(GenericParser):
    def __init__(self):
        super(EngadgetParser, self).__init__()

    source = u"Engadget"
    
    def parse(self, url):

	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        soup.find('p', {'class':'read-more'}).extract()
        
        title = soup.find('h1', {"itemprop": "headline"})
        title = title.text.strip()
        
        
        paragraphs = soup.find('div', {"itemprop": "articleBody"}).findAll('p')
        
        content = ""
        for paragraph in paragraphs:
            content += "\n" + re.sub('^[[][^]]+[]]$', '', paragraph.text.strip())
            #content += "\n" + paragraph.text.strip()
            
        content = content.strip()
        
        #print content
        #exit()
        tags = ["tecnologia"]
        categories=["tecnologia"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
