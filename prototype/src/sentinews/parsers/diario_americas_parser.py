#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from bit_opener import BitOpener
from news_entry import NewsEntry
from src.sentinews.parsers.generic_parser import GenericParser


class DiarioAmericasParser(GenericParser):
    def __init__(self):
        super(DiarioAmericasParser, self).__init__()
        self.opener = BitOpener()

    source = u"Diario de las Americas"

    def is_parseable(self, url, soup=None):
        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))

        category = soup.find('div', {"class": "box_title"})
        for ref in category.findAll('a'):
            ref.extract()
        category = category.text.strip()
        categories_wanted = {u'Portada América Latina', u'Venezuela', u'Cuba', u'Locales', u'La Nación', u'EEUU',
                             u'Inmigración', u'Acercamiento EEUU-Cuba', u'Mundo', u'Portada Deportes', u'NBA',
                             u'Béisbol', u'Fútbol', u'Boxeo', u'Deportes Agencia EFE', u'Portada Dinero', u'Tecnología',
                             u'Ultima Hora'}

        if category not in categories_wanted:
            allowed = False

        title = soup.find('div', {"class": "detailbox"})
        title = title.h1.text

        if u"FOTOGALERÍA" in title:
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

        title = soup.find('div', {"class": "detailbox"})
        title = title.h1.text

        category = soup.find('div', {"class": "box_title"})
        for ref in category.findAll('a'):
            ref.extract()
        categories = [category.text.strip()]

        content = soup.find('div', {"class": "post"})

        #clean twits
        for twit_class in content.findAll(class_=re.compile("twitter")):
            twit_class.extract()

        #clean of any images so the caption wont appear
        for figure in content.findAll(class_=re.compile("image")):
            figure.extract()

        #clean of any photoboxes so the caption wont appear
        for figure in content.findAll(class_=re.compile("photobox")):
            figure.extract()

        #clean unwanted links
        strong_sentences = content.findAll('strong')
        for strong_sentence in strong_sentences:
            if re.match(u"LEA TAMBIÉN", strong_sentence.text):
                strong_sentence.parent.extract()
            elif re.match(u"VIDEO", strong_sentence.text):
                strong_sentence.parent.extract()

        bold_sentences = content.findAll('a', {"href": re.compile(".+")})
        for sentence in bold_sentences:
            if re.match(u"LEA TAMBIÉN", sentence.string):
                sentence.parent.extract()

        #clean video
        for video in content.findAll(src=re.compile("editor.wouzee")):
            video.parent.extract()

        content = content.text
        content = self.sanitize(content)
        assert content.find('function()') == -1

        tags = []

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

