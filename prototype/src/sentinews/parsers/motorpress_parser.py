#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class MotorPressParser(GenericParser):
    def __init__(self):
        super(MotorPressParser, self).__init__()

    source = u"Motor Press"

    def parse(self, url):
        #FIX BROKEN URLS:
        #url = "http://motorpress.com.ar/autosnoticias/ultimas-noticias/peugeot-muestra-el-restyling-del-208-en-brasil"
        url = url.replace("http://motorpress.com.ar/autos", "http://motorpress.com.ar/autos/")
        url = url.replace("autos//", "autos/")

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        #for pics in soup.findAll('div', {'class': 'article_content_photo'}):
        #    pics.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('article', {"class":"content"}).find('h1')
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        intro = soup.find('article',{"class":"content"}).find('h2')

        if intro is not None:
            content = intro.text.strip() + "\n"


        article_content = soup.find('div',{"class": "content-stuff"})

        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        categories = [u"automóviles"]
        tags = [u"automóviles"]

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
