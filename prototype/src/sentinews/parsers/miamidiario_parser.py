#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class MiamiDiarioParser(GenericParser):
    def __init__(self):
        super(MiamiDiarioParser, self).__init__()

    source = u"Miami Diario"

    def is_parseable(self, url, soup=None):
        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))

        category = soup.find('div', {"class": "nombre_seccion"})
        print "Categoria es %s" % category.text
        categories_not_wanted = {u'Guia fin de semana', u'Eventos', u'Farándula', u'Rostro y cuerpo',
                                 u'Trucos de cocina', u'Curiosidades', u'Comunitaria', u'Tránsito', u'Música'}

        if category.text in categories_not_wanted:
            allowed = False

        #extract video
        tag_list = soup.find('div', {"class": "tags"})
        for tag in tag_list.findAll('a'):
            if (tag.text in u'Video') or (tag.text in u'caja de pandora') or (tag.text in u'nuevo video'):
                allowed = False

        if u'/opinion/' in url:
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

        unwanted_titles = {u"También te puede interesar:", u"También le puede interesar leer:",
                           u"Quizás le interese leer:", u"Le puede interesar también:",
                           u"Para más información, visite:", u"Quizás le interese...", u"Le puede interesar:",
                           u"Le puede interesar leer:", u"Disfrútalo aquí"}

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

        new_entry = self.create_news_entry(title, content, tags, self.source, url, categories,
                                           image_search_string)
        return new_entry

