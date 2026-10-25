#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class CientoUnLugaresParser(GenericParser):
    def __init__(self):
        super(CientoUnLugaresParser, self).__init__()

    source = "101 Lugares Increibles"

    def parse(self, url):
        #url = "http://101lugaresincreibles.com/2016/03/7-mejores-playas-de-cerdena-italia.html"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for ads in soup.findAll('div', {'class': 'advads-pie-de-contenidos-varios'}):
            ads.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('h1', {"class":"entry-title"})
        title = title.text.strip()


        #-------------------CONTENT--------------------------
        content = ""

        #ntro = soup.find('p',{"class":"intro"})

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find('div',{"class": "entry-content"})

        paragraphs = article_content.findAll(['p','h2'])

        for paragraph in paragraphs:
            clean_text = re.sub(r"^Copyright:.+$", "", paragraph.text.strip())
            content += "\n" + clean_text


        #print content
        #exit()
        categories = ["turismo"]
        tags = ["turismo"]

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
