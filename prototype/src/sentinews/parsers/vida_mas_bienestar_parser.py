#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class VidaMasBienestarParser(GenericParser):
    def __init__(self):
        super(VidaMasBienestarParser, self).__init__()

    source = u"Vida + Bienestar"

    def parse(self, url):
        #url = "http://vidaybienestar.mx/limpieza-cada-temporada/?utm_source=rss&utm_medium=rss&utm_campaign=limpieza-cada-temporada"
        #url = "http://vidaybienestar.mx/el-calentamiento/"
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for links in soup.findAll('div', {'class': 'essb_links'}):
            links.extract()


        #-------------------TITLE--------------------------
        title = soup.find('h3',{'itemprop':'headline'})
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('article',{"class":"content"}).find('h2')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find('div',{'class':'entry'})

        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        categories = [u"salud"]
        tags = [u"salud"]

        #categories=[urlparse(url).path.split("/")[1]]
        #print categories
        #return {"content":content, "title":title}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
