#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class SportlifeParser(GenericParser):
    def __init__(self):
        super(SportlifeParser, self).__init__()

    source = u"Sportlife"

    def parse(self, url):
        #url = "http://www.sportlife.es/rss/sportlife/articulo/du-cross-series-estrena-duatlon-carretera"

	#20160119 - Daniel Cantarín
        #FIX: sportlife construye las URLs con un error de sintaxis menor. Lo arreglo.
        tmp1 = url.split("://")
        tmp2 = tmp1[1].replace("//","/")
        url  = tmp1[0] + "://" + tmp2

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()

        title = soup.find("h1").text.strip()

        content = ""
        article_content = soup.find("div", {"class", "texto-articulo"})

        paragraphs = article_content.findAll("p")

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        content = content.strip()

        if content == "" :
            content = article_content.text.strip()

        #return {"title" : title , "content" : content}
        categories = []
        tags = []

        tags = ["fitness"]
        categories=["salud"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
