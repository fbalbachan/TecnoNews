#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser

class GenbetaParser(GenericParser):
    def __init__(self):
        super(GenbetaParser, self).__init__()

    source = "Genbeta"
    
    def parse(self, url):

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')

        for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
            
        for video in soup.findAll('div', {'class':'js-video'}):
            video.extract()
        
        
        title = soup.find('h1')
        title = title.text.strip()
        
        paragraphs = soup.find('div', {"class": "article-content"}).find('div', {'class': "blob"}).findAll('p')
        
        while "|" in paragraphs[-1].text:
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
