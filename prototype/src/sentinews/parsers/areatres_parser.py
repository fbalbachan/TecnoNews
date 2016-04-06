#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class AreaTresParser(GenericParser):
    def __init__(self):
        super(AreaTresParser, self).__init__()

    source = u"Real Estate Market"

    def parse(self, url):
        url = "http://www.revistaareatres.com.ar/novedades/index/restricciones-que-afectan-a-la-construccion"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()

        #-------------------TITLE--------------------------
        title = soup.find('h2')
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('h3')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find('div',{'class':'contenido'})

        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        print content
        exit()
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

testParser = AreaTresParser()
testParser.parse("a")
