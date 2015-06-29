#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from bit_opener import BitOpener
from news_entry import NewsEntry
from urlparse import urlparse

class InformadorParser(object):
    def __init__(self):
        super(InformadorParser, self).__init__()
        self.opener = BitOpener()

    source = u"Informador"

    def is_parseable(self, url, soup=None):
        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))


        # category = soup.find('div', {"class" : "nombre_seccion"})
        # print "Categoria es %s" % category.text
        # categories_not_wanted = set([u'Guia fin de semana',
        #                         u'Eventos',
        #                         u'Farándula',
        #                         u'Rostro y cuerpo',
        #                         u'Trucos de cocina',
        #                         u'Curiosidades'])

        # if category.text in categories_not_wanted:
        #     allowed = False

        # #extract video
        # tag_list = soup.find('div',{"class":"tags"})
        # for tag in tag_list.findAll('a'):
        #     if tag.text in u'Video':
        #         allowed = False

        # title = soup.find('div', {"class": "detailbox"})
        # title = title.h1.text

        # if (u"FOTOGALERÍA" in title):
        #     allowed = False


        return allowed


    def parse(self, url):

        soup = BeautifulSoup(self.opener.read(url))

        if not self.is_parseable(url=url, soup=soup):
            return None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        image_search_string = None

        title = soup.find('div', {"class": "tituloInt"})
        title = title.h1.text

        
        categories=[urlparse(url).path.split("/")[1]]

        content = soup.find('div', {"id" : "HOTWordsTxt"})

        #arranco el lugar y fecha del texto
        place_date = content.find('strong')
        place_date.extract()        
        # unwanted_titles = set([u"También te puede interesar:",
        #                     u"También le puede interesar leer:",
        #                     u"Quizás le interese leer:",
        #                     u"Le puede interesar también:"])

        # #clean unwanted links
        # for tambien in content.findAll('strong'):
        #     if tambien.text in unwanted_titles:
        #         tambien.extract()

        # for tambien in content.findAll('b'):
        #     if tambien.text in unwanted_titles:
        #         tambien.extract()

        # unwanted_links = content.findAll('a',{"href":re.compile(".+")})
        # for links in unwanted_links:
        #     links.extract()

        tag_list = soup.find('div',{"id":"temasNoticia"})
        tags = []
        for tag in tag_list.findAll('a'):
            tags.append(tag.text)


        content = content.text

        #gb: lo dejo por las dudas pero no encontre ejemplos con js
        assert content.find('function()') == -1

        

        

        new_entry = NewsEntry(title=title, content=content,
                                    tags=tags,
                                    source=self.source,
                                    url=url,
                                    original_categories=categories,
                                    image_search_string=image_search_string)

        if not new_entry:
            print(u"Couldn't parse news in CNet Español ")
            print(u"Url: %s " % url)

        return new_entry

