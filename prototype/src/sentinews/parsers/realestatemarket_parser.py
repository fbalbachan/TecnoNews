#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class RealEstateMarketParser(GenericParser):
    def __init__(self):
        super(RealEstateMarketParser, self).__init__()

    source = u"Real Estate Market"

    def parse(self, url):
        #url = "http://realestatemarket.com.mx/noticias/infraestructura-y-construccion/18654-aumenta-1-inversion-fija-bruta-en-enero"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()

        #-------------------TITLE--------------------------
        title = soup.find('h2', {'itemprop':'name'})
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('h3')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find('div',{'itemprop':'articleBody'})

        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        categories = [u"propiedades"]
        tags = [u"propiedades"]

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
