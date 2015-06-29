#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from news_entry import NewsEntry
from src.sentinews.parsers.generic_parser import GenericParser


class CNetEspParser(GenericParser):
    def __init__(self):
        super(CNetEspParser, self).__init__()

    source = u"CNet Español"

    def parse(self, url):
        
        if (u'/imagenes/' in url) or (u'/videos/' in url) or (u'/analisis/' in url):
            return None

        soup = BeautifulSoup(self.opener.read(url))

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        image_search_string = None

        title = soup.find('h1', {"itemprop": "headline"})
        title = title.text.strip()

        metadata = soup.find('ul', {"class" : "breadcrumb"})
        categories = []
        for category in metadata.findAll(href=re.compile("/es/temas/")):
            categories.append(category.text.strip())

        tags_div = soup.find('div', {"class" : "row collections-topics-and-tags", "section" : "tag"})
        tags = []
        for tag in tags_div.findAll(href=re.compile("/es/temas/")):
            tags.append(tag.text.strip())

        content = soup.find('div', {"class" : "article-main-body row","itemprop": 'articleBody'})
        
        #clean relate links from content
        for related_link in content.findAll('div', {"section" : "shortcodeRelatedLinks"}):
            related_link.extract()
        #clean any inpage videos from content
        for video in content.findAll(class_=re.compile("video")):
            video.extract()
        #clean any inpage galleries from content
        for gallery in content.findAll(class_=re.compile("gallery")):
            gallery.extract()
        #clean of any figures so the caption wont appear
        for figure in content.findAll('figure'):
            figure.extract()
         #clean of twits in content
        for twit in content.findAll(class_=re.compile("twitter")):
            twit.extract()


        content = content.text
        content = self.sanitize(content)
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

