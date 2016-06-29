#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class MundoReciclajeParser(GenericParser):
    def __init__(self):
        super(MundoReciclajeParser, self).__init__()

    source = u"El mundo del reciclaje"

    def parse(self, url):
        #url = "http://elmundodelreciclaje.blogspot.com.ar/2016/06/recicla-palets-y-disfruta-de-tu-jardin.html"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        #for pics in soup.findAll('div', {'class': 'article_content_photo'}):
        #    pics.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('h3', {"class":"post-title"})
        title = title.text.strip()
        #print title
        #exit()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('article',{"class":"content"}).find('h2')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find('div',{"class": "entry-content"}).stripped_strings

        #paragraphs = article_content.findAll(['p', 'h2'])

        for paragraph in article_content:
            clean_text = paragraph.strip()
            content += "\n" + clean_text

        #print content
        #exit()
        categories = [u"zolvers"]
        tags = [u"zolvers"]

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
