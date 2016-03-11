#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re



class CicConstruccionParser(GenericParser):
    def __init__(self):
        super(CicConstruccionParser, self).__init__()

    source = u"CicConstruccion"
    
    def parse(self, url):
        #url = "http://www.cicconstruccion.com/es/notices/2015/12/euroconstruct-preve-que-la-construccion-crecera-en-espana-un-4-4-en-2016-67908.php#.VnQcKV5vthE"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
            
            
        title = soup.find('div',{'class':'ext_news_title'})
        title =  title.text.strip()
       
        content = "" 
        
        intro = soup.find('div',{'class':'ext_news_avantitle'})
        if intro:
            content = intro.text.strip() + "."
        
        paragraphs = soup.find('div',{'class':'ext_news_body'}).findAll('p')
        
        
        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()

                
            content += "\n" + clean_text

        
        content = content.strip()

        tags = ["propiedades"]
        categories=["propiedades"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
