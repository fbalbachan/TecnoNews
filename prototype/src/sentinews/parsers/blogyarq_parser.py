#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class BlogYArqParser(GenericParser):
    def __init__(self):
        super(BlogYArqParser, self).__init__()

    source = u"Blog y Arquitectura"

    def parse(self, url):
        #url = "http://blogyarq.blogspot.com.ar/2016/03/coleccion-muffin-stone-designs.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed:+Blogyarquitectura+%28Blog+y+Arquitectura%29&utm_content=FeedBurner"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        #for links in soup.findAll('div', {'class': 'essb_links'}):
        #    links.extract()


        #-------------------TITLE--------------------------
        title = soup.find('h1',{'class':'entry-title'})
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('article',{"class":"content"}).find('h2')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        content = soup.find('div',{'class':'entry-content'}).text.strip()


        categories = [u"propiedades"]
        tags = [u"propiedades"]

        #categories=[urlparse(url).path.split("/")[1]]
        #print categories

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
