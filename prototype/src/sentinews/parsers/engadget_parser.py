#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class EngadgetParser(GenericParser):
    def __init__(self):
        super(EngadgetParser, self).__init__()

    source = "Engadget"
    
    def parse(self, url):
        #url  = "http://es.engadget.com/2016/06/06/cortana-xbox-one-nueva-actualizacion/"
        #url  = "http://es.engadget.com/2016/06/06/kingston-datatraveler-2000-pendrive-mas-seguro-del-mundo/"
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        for p in soup.findAll('p', {'class':'read-more'}):
            p.extract()
        
        title = soup.find('h1', {"class": "post-title"})
        title = title.text.strip()
        
        
        paragraphs = soup.find('div', {"class": "m-permalink-post-data"}).findAll('p')
        
        content = ""
        for paragraph in paragraphs:
            content += "\n" + re.sub('^[[][^]]+[]]$', '', paragraph.text.strip())
            #content += "\n" + paragraph.text.strip()
            
        content = content.strip()
        
        #print content
        #exit()
        tmptags    = soup.find("div",{"class":"post-meta-tags"}).findAll("a")
        tags       = ["tecnologia"]
        categories = ["tecnologia"]

        for t in tmptags:
            tags.append( t.text.strip() )

        #return {"tags":tags,"content":content,"title":title}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
