#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class BlogHogarParser(GenericParser):
    def __init__(self):
        super(BlogHogarParser, self).__init__()

    source = u"Blog Hogar"

    def parse(self, url):
        #url = "http://bloghogar.com/la-importancia-de-escoger-una-buena-empresa-de-mudanzas/"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        #for pics in soup.findAll('div', {'class': 'article_content_photo'}):
        #    pics.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('h1', {"class":"entry-title"})
        title = title.text.strip()
        #print title
        #exit()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('article',{"class":"content"}).find('h2')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find('section',{"class": "entry-content"})

        paragraphs = article_content.findAll(['p', 'h2'])

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        #print content
        #exit()
        categories = [u"zolvers"]
        tags = [u"zolvers"]

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
