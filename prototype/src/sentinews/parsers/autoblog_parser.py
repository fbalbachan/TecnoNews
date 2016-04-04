#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class AutoBlogParser(GenericParser):
    def __init__(self):
        super(AutoBlogParser, self).__init__()

    source = u"Auto Blog"

    def parse(self, url):
        #url = "http://autoblog.com.ar/2016/04/04/el-gobierno-despidio-al-disenador-de-la-nueva-patente-mercosur/"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        #for pics in soup.findAll('div', {'class': 'article_content_photo'}):
        #    pics.extract()

        #return soup


        #-------------------TITLE--------------------------
        title = soup.find('h1', {"class":"post-title"})
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('article',{"class":"content"}).find('h2')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find('div',{"class": "entry-inner"})

        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            if clean_text == "***":
                break
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
