#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser

class XatakaParser(GenericParser):
    def __init__(self):
        super(XatakaParser, self).__init__()

    source = u"Xataka"
    
    def parse(self, url):
        #url = "http://www.xataka.com/empresas-y-economia/no-dependemos-del-pc-a-intel-le-va-bien-gracias-a-los-servidores-y-la-nube?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+xataka2+%28Xataka%29"
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.find('h1', {"class": "article-header"})
        title = title.text.strip()
        #print title
        
        paragraphs = soup.find('div', {"class": "article-summary"}).findAll('p')
        
        paragraphs.pop()
        
        content = ""
        for paragraph in paragraphs:
            content += "\n" + paragraph.text.strip()
            
        content = content.strip()
        
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
