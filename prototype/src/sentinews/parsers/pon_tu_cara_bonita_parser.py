#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from src.sentinews.parsers.generic_parser import GenericParser
import re

class PonTuCaraBonitaParser(GenericParser):
    def __init__(self):
        super(PonTuCaraBonitaParser, self).__init__()

    source = "Pon tu cara bonita"

    def parse(self, url):
        #url= "http://www.portucarabonita.com/2015/12/ideas-de-regalos-very-cute.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+PorTuCaraBonitaBlogDeBellezaModaYReviewsDeProductos+%28Por+tu+cara+bonita+|+Blog+de+belleza%2C+moda+y+lifestyle%29&utm_content=FeedBurner"

        soup = BeautifulSoup(self.opener.read(url),
                             from_encoding='utf-8')

        image_search_string = None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        title = soup.find('h3', {"class": "post-title entry-title"})
        title = title.text.strip()        


        
        content = ""

        content = soup.find('div', {"itemprop": 'description articleBody'}).text.strip()

        tags = ["belleza"]
        categories = ["belleza"]


        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry
