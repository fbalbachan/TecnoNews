#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class TrendenciasLifeStyleParser(GenericParser):
    def __init__(self):
        super(TrendenciasLifeStyleParser, self).__init__()

    source = u"Trendencias Lifestyle"

    def parse(self, url):
        #url = "http://lifestyle.trendencias.com/tecnologia-y-gadgets/floatti-tras-los-smartphones-los-smartwatches-o-las-smartcases-llega-la-smartsuitcase"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()


        for links in soup.findAll('div', {'class': 'article-links'}):
            links.extract()


        #-------------------TITLE--------------------------
        title = soup.find('h1')
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('article',{"class":"content"}).find('h2')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find('div',{'class':'article-content'})

        paragraphs = article_content.findAll('p')

        while "|" in paragraphs[-1].text:
            paragraphs.pop()

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        categories = [u"rojovida"]
        tags = [u"rojovida"]

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
