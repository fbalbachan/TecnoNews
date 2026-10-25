#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re


class GlamourParser(GenericParser):
    def __init__(self):
        super(GlamourParser, self).__init__()

    source = "Glamour"

    def parse(self, url):
        if "/galerias/" in url:
            return None
        # url = "http://www.glamour.es/belleza/cuerpo/articulos/la-dieta-feng-shui-tu-cocina-te-esta-haciendo-engordar-1/22478"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()

        for image in soup.findAll('img'):
            image.extract()

        for tags in soup.findAll('div', {'class': 'tags'}):
            tags.extract()

        for dates in soup.findAll('p', {'class': 'date'}):
            dates.extract()

        for related in soup.findAll('div', {'class': 'related-articles hightlighted'}):
            related.extract()

        for trash in soup.findAll(True, {"class": ["footer"]}):
            trash.extract()

        title = soup.find('h1', {'class': ['heading', 'headline']})
        # title = soup.find('article').find('h1')
        title = title.text.strip()
        # print title
        # exit()

        content = ""

        # intro = soup.find('div',{'class':'excerpt'})
        # if intro:
        #    content = intro.text.strip()

        paragraphs = soup.find('div', {'class': 'content'}).findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()

            content += "\n" + clean_text

        content = content.strip()

        # content = soup.find('div',{'class':'post-body entry-content'}).text
        # content = re.sub(u'\nFuentes?:.+\n','',content)
        # content = re.sub(u'\n(Extranotix\.|Tu opinión|Enviar por correo electrónico.+)\n','',content)
        # content = re.sub(u'\n\n+','\n',content).strip()

        tags = ["entretenimiento"]
        categories = ["entretenimiento"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
