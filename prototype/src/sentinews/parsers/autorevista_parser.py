#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class AutoRevistaParser(GenericParser):
    def __init__(self):
        super(AutoRevistaParser, self).__init__()

    source = u"Auto Revista"

    def parse(self, url):
        #url = "http://www.auto-revista.com/es/notices/2016/03/seat-martorell-abre-mas-oportunidades-a-proveedores-con-un-todocamino-en-2017-119431.php"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()

        #-------------------TITLE--------------------------
        title = soup.find(True,{'class':'ext_news_title'})
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('h3')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        content = soup.find(True,{'class':'ext_news_body'}).text

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
