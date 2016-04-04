#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class ExpresoParser(GenericParser):
    def __init__(self):
        super(ExpresoParser, self).__init__()

    source = u"Expreso"

    def parse(self, url):
        #url = "http://www.expreso.info/noticias/biblioteca/49583_editada_la_guia_de_visita_del_parque_nacional_de_cabaneros"

	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()


        title = soup.find('a',{'class':re.compile("titulo_xx.*")})
        title =  title.text.strip()

        content = ""

        paragraphs = soup.find('div',{'class':'node'}).find('div',{'class':'content'}).findAll(['p','div'])
        paragraphs.pop()


        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()


            content += "\n" + clean_text


        content = content.strip()


        tags = [u"rojotur"]
        categories=[u"rojotur"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
