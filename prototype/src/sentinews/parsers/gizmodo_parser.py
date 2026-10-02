#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser

class GizmodoParser(GenericParser):
    def __init__(self):
        super(GizmodoParser, self).__init__()

    source = "Gizmodo"
    
    def parse(self, url):
        #url = "http://es.gizmodo.com/he-usado-el-ipad-pro-como-sustituto-total-de-mi-portati-1743773109"
        #url = "http://es.gizmodo.com/secuestran-el-twitter-de-mark-zuckerberg-segun-los-hac-1780743041"
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        #soup = BeautifulSoup(self.opener.read(url))

        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        for adv in soup.findAll('aside', {"class": "referenced-wide referenced-fullwidth js_inset tmpl_referencedGroupFullWidth clearfix core-decorated-inset"}):
            adv.extract()
            
        for hidden in soup.findAll('a', {"x-inset": "hidden"}):
            hidden.extract()

        title = soup.find('h1', {"class": "headline hover-highlight entry-title js_entry-title"})
        title = title.text.strip()
        #print title

        paragraphs = soup.find('div', {"class": "post-content"}).findAll('p')
        
        #paragraphs.pop()
        content = ""
        for paragraph in paragraphs:
            content += "\n" + paragraph.text.strip()
            
        content = content.strip()
        
        tags = ["tecnologia"]
        categories=["tecnologia"]
        #return {"tags":tags, "title":title,"content":content}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
