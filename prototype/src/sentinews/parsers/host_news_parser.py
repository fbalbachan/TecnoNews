#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class HostNewsParser(GenericParser):
    def __init__(self):
        super(HostNewsParser, self).__init__()

    source = u"Host News"
    
    def parse(self, url):
        #url = "http://hostnews.com.ar/index.php/news/12340/16"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
            
            
        title = soup.find('div',{'id':'contenido'}).find('h1')
        title =  title.text.strip()
        
        
        content = "" 
        
        intro = soup.find('div',{'id':'contenido'}).find('div',{'id':'NewsPostDetailSummary'})
        if intro:
            content += intro.text.strip()# + "."
            
        paragraphs = soup.find('div',{'id':'contenido'}).find('div',{'id':'NewsPostDetailContent'})
        
        content += "\n" + re.sub(u'([^ ]+)[.][ ]*([A-Z“][^A-Z ]*)', r'\1.\n\2', paragraphs.text.strip()) #REEMPLAZA finparrafo.NuevoParrafo => finparrafo.\n NuevoParrafo

        
        content = content.strip()
        
        tags = []
        categories=[u"interés general"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
        
