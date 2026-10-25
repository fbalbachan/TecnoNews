#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class MariaLeonStyleParser(GenericParser):
    def __init__(self):
        super(MariaLeonStyleParser, self).__init__()

    source = "Maria Leon Style"

    def parse(self, url):
        #url = "http://www.marialeonstyle.com/lifestyle/un-viaje-con-estilo-por-peru-by-maria-leon-style-2/"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for caption in soup.findAll('p', {'class': 'wp-caption-text'}):
            caption.extract()


        #-------------------TITLE--------------------------
        title = soup.find(True, {"class":"entry-title"})
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

        categories = ["belleza"]
        tags = ["belleza"]

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
