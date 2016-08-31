#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class NuevoHeraldParser(GenericParser):
    def __init__(self):
        super(NuevoHeraldParser, self).__init__()

    source = u"Nuevo Herald"

    def is_parseable(self, url, soup=None):
        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))

        if (u'/opinion-es/' in url) or (u'/vivir-mejor/' in url) or (u'/dep-col-blogs/' in url) \
                or (u'/ent-columnistas-blogs/' in url):
                allowed = False

        title = soup.find('h1', {"class": "title"})
        title = title.text.strip()

        #the article is a photo gallery
        if (u"GALERÍA" in title) or (u"MUNDO EN IMÁGENES" in title) or (u"VIDEO" in title):
            return None

        return allowed

    def parse(self, url):

        soup = BeautifulSoup(self.opener.read(url))

        if not self.is_parseable(url=url, soup=soup):
            return None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        image_search_string = None

        #collet keywords from meta tags
        keywords_set=set()
        for keywords in soup.findAll('meta', {"name":re.compile("keywords")}):
            keywords_set.update([word.strip() for word in keywords['content'].split(',')])


        title = soup.find('h1', {"class": "title"})
        title = title.text.strip()

        category = soup.find(class_=re.compile("section-main-heading"))
        categories = [category.text.strip()]

        content = soup.find(id=re.compile("content-body"))

        #clean endnote contact
        for endnote in content.findAll(class_=re.compile("endnote")):
            endnote.extract()

        #clean media from content
        for media in content.findAll(class_=re.compile("media")):
            media.extract()

        #clean twitter strings
        strong_sentences = content.findAll('strong')
        for strong_sentence in strong_sentences:
            if re.search(u'en twitter:',strong_sentence.text):
                strong_sentence.parent.extract()

        #clean factbox contact
        for factbox in content.findAll(class_=re.compile("ng_factbox")):
            factbox.extract()

        paragraphs = content.findAll('p')
        content = ''
        for p in paragraphs:
            content += p.text + '\n'

        tags = []
        keywords = list(keywords_set)

        new_entry = self.create_news_entry(title=title, content=content,
                                    tags=tags,
                                    source=self.source,
                                    url=url,
                                    original_categories=categories,
                                    image_search_string=image_search_string,
                                    keywords=keywords)

        return new_entry
