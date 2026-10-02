#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class PlanetaCuriosoParser(GenericParser):
    def __init__(self):
        super(PlanetaCuriosoParser, self).__init__()

    source = "Planeta Curioso"
    
    def parse(self, url):
        #url = "http://www.planetacurioso.com/2016/01/25/air-bonsai-los-curiosos-bonsais-que-flotan-causan-sensacion-todos-quieren-uno/"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        for sumario in soup.findAll('div',{'class':'sumario mobile-center '}):
            sumario.extract()
            
        for ads in soup.findAll('div',{'class':'entry-ads-left'}):
            ads.extract()
        
        #title = soup.find('p',{'class':'title'})
        title = soup.find('article').find('h1')
        title =  title.text.strip()
        #print title
        #exit()

        content = "" 
        
        intro = soup.find('div',{'class':'excerpt'})
        if intro:
            content = intro.text.strip()
        
        
        paragraphs = soup.find('div',{'class':'entry'}).findAll('p')
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()

                
            content += "\n" + clean_text

        
        content = content.strip()

        #print content
        #exit()

        tags = ["insólito"]
        categories=["insólito"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
