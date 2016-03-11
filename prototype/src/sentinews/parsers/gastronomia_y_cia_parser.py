#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser

class GastronomiaYCiaParser(GenericParser):
    def __init__(self):
        super(GastronomiaYCiaParser, self).__init__()

    source = u"GastronomiaYCia"


    def parse(self, url):
        #url = "http://www.gastronomiaycia.com/2015/12/02/cervezas-galardonadas-en-cica-2015/"
        
	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.find('h1', {'class':'entry-title'})
        title =  title.text.strip()
        
        content = "" 
        
        intro = soup.find('p', {'class':'entry-excerpt'})
        if intro:
            content = intro.text.strip()

        
        paragraphs = soup.find('div',{'itemprop':'articleBody'}).findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()

                
            content += "\n" + clean_text

        
        content = content.strip()
        
        
        categories = []
        raw_categories = soup.find('p',{'class':'entry-categories'})
        if raw_categories != None:
            raw_categories = raw_categories.findAll('a')
            for category in raw_categories:
                categories.append(category.text.strip())
        
        tags = []
        raw_tags = soup.find('ul',{'class':'entry-tags'})
        if raw_tags != None:
            raw_tags = raw_tags.findAll('a')
            for tag in raw_tags:
                tags.append(tag.text.strip())

        tags = ["estilo vida"]
        categories=["estilo vida"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
