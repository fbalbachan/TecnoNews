#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class DiarioAmericasParser(GenericParser):
    def __init__(self):
        super(DiarioAmericasParser, self).__init__()

    source = "Diario de las Americas"

    def is_parseable(self, url, soup=None):
        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))

        category = soup.find('div', {"class": "box_title"})
        for ref in category.findAll('a'):
            ref.extract()
        category = category.text.strip()
        categories_wanted = {'Portada América Latina', 'Venezuela', 'Cuba', 'Locales', 'La Nación', 'EEUU',
                             'Inmigración', 'Acercamiento EEUU-Cuba', 'Mundo', 'Portada Deportes', 'NBA',
                             'Béisbol', 'Fútbol', 'Boxeo', 'Deportes Agencia EFE', 'Portada Dinero', 'Tecnología',
                             'Ultima Hora'}

        if category not in categories_wanted:
            allowed = False

        title = soup.find('div', {"class": "detailbox"})
        title = title.h1.text

        if "FOTOGALERÍA" in title:
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
            if re.match("LEA TAMBIÉN", strong_sentence.text):
                strong_sentence.parent.extract()
            elif re.match("VIDEO", strong_sentence.text):
                strong_sentence.parent.extract()

        bold_sentences = content.findAll('a', {"href": re.compile(".+")})
        for sentence in bold_sentences:
            if re.match("LEA TAMBIÉN", sentence.string):
                sentence.parent.extract()

        #clean video
        for video in content.findAll(src=re.compile("editor.wouzee")):
            video.parent.extract()

        #take out first paragraph that contais date, author, city
        first_paragraph = content.find('p')
        first_paragraph.extract()

        tags = []
        p_content = ''
        for p in content.findAll('p'):
            p_content += p.text + '\n'

        content = p_content
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry

