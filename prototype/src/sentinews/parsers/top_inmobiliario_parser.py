#!/usr/bin/python
# -*- coding: utf-8 -*-




from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class TopInmobiliarioParser(GenericParser):
    def __init__(self):
        super(TopInmobiliarioParser, self).__init__()

    source = u"TopInmobiliario"
    
    def parse(self, url):
        #url = "http://www.topinmobiliario.com/blog/index.php/capitales-privados-y-publicos-buscan-recuperar-el-barrio-de-la-boca/"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        for caption in soup.findAll('p',{'class':'wp-caption-text'}):
            caption.extract()
            
            
        title = soup.find('h2')
        title =  title.text.strip()


        content = "" 
        
        
        
        paragraphs = soup.find('div',{'class':'textcontent'}).findAll('p')
        
        if(paragraphs[-1].text.find('Publicado en')):
            paragraphs.pop()
        
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
