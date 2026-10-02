#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class MiamiDiarioParser(GenericParser):
    def __init__(self):
        super(MiamiDiarioParser, self).__init__()

    source = "Miami Diario"

    def is_parseable(self, url, soup=None):
        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))

        category = soup.find('div', {"class": "nombre_seccion"})
        categories_not_wanted = {'Guia fin de semana', 'Eventos', 'Farándula', 'Rostro y cuerpo',
                                 'Trucos de cocina', 'Curiosidades', 'Comunitaria', 'Tránsito', 'Música'}

        if category.text in categories_not_wanted:
            allowed = False

        #extract video
        tag_list = soup.find('div', {"class": "tags"})
        for tag in tag_list.findAll('a'):
            if (tag.text in 'Video') or (tag.text in 'caja de pandora') or (tag.text in 'nuevo video'):
                allowed = False

        if '/opinion/' in url:
            allowed = False

        return allowed

    def parse(self, url):

        soup = BeautifulSoup(self.opener.read(url))

        if not self.is_parseable(url=url, soup=soup):
            return None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        image_search_string = None

        title = soup.find('div', {"class": "titulo_noticia_desarrollada"})
        title = title.text

        category = soup.find('div', {"class": "nombre_seccion"})

        categories = [category.text]

        content = soup.find('div', {"class": "desarrollo_noticia"})

        unwanted_titles = {"También te puede interesar:", "También le puede interesar leer:",
                           "Quizás le interese leer:", "Le puede interesar también:",
                           "Para más información, visite:", "Quizás le interese...", "Le puede interesar:",
                           "Le puede interesar leer:", "Disfrútalo aquí"}

        #clean unwanted links
        for tambien in content.findAll('strong'):
            if tambien.text in unwanted_titles:
                tambien.extract()

        for tambien in content.findAll('b'):
            if tambien.text in unwanted_titles:
                tambien.extract()

        for tambien in content.findAll('em'):
            if tambien.text in unwanted_titles:
                tambien.extract()

        unwanted_links = content.findAll('a', {"href": re.compile(".+")})
        for links in unwanted_links:
            links.extract()

        #clean twits
        for twit in content.findAll(class_=re.compile('twitter-tweet')):
            twit.extract()

        #clean frames that contain videos
        for frame in content.findAll('iframe'):
            frame.extract()

        tag_list = soup.find('div', {"class": "tags"})
        tags = []
        for tag in tag_list.findAll('a'):
            tags.append(tag.text)

        content = content.text.strip()

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)
        return new_entry

