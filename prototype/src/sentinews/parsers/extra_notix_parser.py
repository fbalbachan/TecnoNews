#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class ExtraNotixParser(GenericParser):
    def __init__(self):
        super(ExtraNotixParser, self).__init__()

    source = u"Extra Notix"
    
    def parse(self, url):
        #url = "http://extranotix.blogspot.com/2016/01/un-virus-mortal-causa-20-muertos-y-mas.html"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        for sumario in soup.findAll('div',{'class':'sumario mobile-center '}):
            sumario.extract()
            
        for ads in soup.findAll('div',{'class':'entry-ads-left'}):
            ads.extract()
        
        title = soup.find('h3',{'class':'post-title entry-title'})
        #title = soup.find('article').find('h1')
        title =  title.text.strip()
        #print title
        #exit()

        content = "" 
        
        #intro = soup.find('div',{'class':'excerpt'})
        #if intro:
        #    content = intro.text.strip()
        
        
        #paragraphs = soup.find('div',{'class':'post-body entry-content'}).findAll('p')
        
        #for paragraph in paragraphs:
        #    clean_text = paragraph.text.strip()

                
        #    content += "\n" + clean_text

        
        #content = content.strip()
        
        content = soup.find('div',{'class':'post-body entry-content'}).text
        content = re.sub(u'\nFuentes?:.+\n','',content)
        content = re.sub(u'\n(Extranotix\.|Tu opinión|Enviar por correo electrónico.+)\n','',content)
        content = re.sub(u'\n\n+','\n',content).strip()
        #print content
        #exit()

        tags = [u"insólito"]
        categories=[u"insólito"]
        
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
