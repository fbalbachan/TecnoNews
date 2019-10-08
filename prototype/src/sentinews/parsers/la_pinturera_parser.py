#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse
from src.sentinews.parsers.generic_parser import GenericParser
import re

class LaPintureraParser(GenericParser):
    def __init__(self):
        super(LaPintureraParser, self).__init__()

    source = u"La Pinturera"

    def parse(self, url):
        # url= "http://www.lapinturera.com/2016/01/verde-mentatambien-en-invierno-look.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Lapinturera-BlogDeCosmticaMaquillajeYBelleza+%28lapinturera+-+Blog+de+cosm%C3%A9tica%2C+maquillaje+y+belleza.%29&utm_content=FeedBurner"
        soup = BeautifulSoup(self.opener.read(url),
                             from_encoding='utf-8')

        image_search_string = None

        for script in soup(["script", "style"]):
            script.extract()

        title = soup.find('h3', {"class": "post-title entry-title"})
        title = title.text.strip()

        content = soup.find('div', {"class": 'post-body'}).text
        content = re.sub(u'¡¡BESOS!!', '', content).strip()
        content = '\n'.join([line for line in content.splitlines() if line.strip()])
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
