#!/usr/bin/python
# -*- coding: utf-8 -*-

#{ "url" : [ "http://www.pronto.com.ar/rss/famosos" ], "default_tags" : null, "parser" : "pronto_parser.ProntoParser", "lastupdated" : ISODate("2016-01-27T02:01:07.174Z"), "id" : "pronto" }

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class ProntoParser(GenericParser):
    def __init__(self):
        super(ProntoParser, self).__init__()

    source = "Pronto"

    def parse(self, url):
        #url = "http://www.pronto.com.ar/articulo/famosos/alfredo-caseros-protagonizo-escandalo-policial-casa-ex-mujer/20160127153351202196.html"
        #url = "http://www.pronto.com.ar/articulo/famosos/famosa-rubia-confiesa-miro-peliculas-porno-sacar-ideas/20160607112825214023.html"
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()


        title = soup.select('h1.title')[0].text.strip()

        content = ""
        article_content = soup.select('article')[0]

        paragraphs = article_content.findAll('p',{"style":None})

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        content = content.strip()

        categories = []
        tags = []

        tags = ["entretenimiento"]
        categories=["entretenimiento"]
        #return {"title":title, "content":content}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
