#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class TravelerParser(GenericParser):
    def __init__(self):
        super(TravelerParser, self).__init__()

    source = u"Traveler"

    def parse(self, url):
        #url = "http://www.traveler.es/viajes/viajes-urbanos/articulos/cosas-que-debes-saber-antes-de-viajar-a-cuba/8582"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for pics in soup.findAll('div', {'class': 'article_content_photo'}):
            pics.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('div', {"class":"article_title"})
        title = title.text.strip()


        #-------------------CONTENT--------------------------
        content = ""

        intro = soup.find('div',{"class":"article_intro"})

        if intro is not None:
            content = intro.text.strip() + "\n"


        article_content = soup.find('div',{"class": "article_text"})

        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            if clean_text.find(u"Puede que también te interese...") != -1:
                break
            content += "\n" + clean_text


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
