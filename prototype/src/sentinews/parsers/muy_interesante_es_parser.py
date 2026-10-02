#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class MuyInteresanteEsParser(GenericParser):
    def __init__(self):
        super(MuyInteresanteEsParser, self).__init__()

    source = "Muy Interesante Español"
    
    def parse(self, url):
        #url = "http://feedproxy.google.com/~r/Muyinteresantees/~3/t45FyQWfCzg/story01.htm"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        for sumario in soup.findAll('div',{'class':'sumario mobile-center '}):
            sumario.extract()
            
        for ads in soup.findAll('div',{'class':'entry-ads-left'}):
            ads.extract()
        
        title = soup.find('h1',{'id':['title_article','title_pyr']})
        #title = soup.find('article').find('h1')
        title =  title.text.strip()
        #print title
        #exit()

        content = "" 
        
        #intro = soup.find('div',{'class':'excerpt'})
        #if intro:
        #    content = intro.text.strip()
        
        
        paragraphs = soup.find('div',{'itemprop':'articleBody'}).findAll('p')
        
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
