#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class AutoBildParser(GenericParser):
    def __init__(self):
        super(AutoBildParser, self).__init__()

    source = u"Auto Bild"

    def parse(self, url):
        #url = "http://www.autobild.es/noticias/subaru-wrx-sti-brutal-batir-record-isla-man-286183"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for view in soup.findAll('div', {'class': 'view-header'}):
            view.extract()

        for quote in soup.findAll('blockquote'):
            quote.extract()

        for noise in soup.findAll(True, {'class': ['publicidad', 'block_galeria']}):
            noise.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('div', {"class":"notice-detalle"}).find('h1')
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('article',{"class":"content"}).find('h2')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find(True,{'itemprop':'articleBody'})

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
