#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser
from src.utils.logger_utils import get_crawler_logger

logger = get_crawler_logger()


class CNetEspParser(GenericParser):
    def __init__(self):
        super(CNetEspParser, self).__init__()

    source = u"CNet Español"

    def parse(self, url):

        if (u'/imagenes/' in url) or (u'/videos/' in url) or (u'/analisis/' in url) or (u'cazadores-de-ofertas' in url):
            return None

        soup = BeautifulSoup(self.opener.read(url))

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        for trash in soup.findAll(True, {"class": ["sharebarWrapper", "caption", "videoContainer"]}):
            trash.extract()

        image_search_string = None

        # title = soup.find('h1', {"itemprop": "headline"})
        title = soup.find('h1')
        title = title.text.strip()

        metadata = soup.find('div', {"class": "authorInfo"})
        categories = []
        for category in metadata.findAll(href=re.compile('/es/temas/')):
            categories.append(category.text.strip())

        tags_div = soup.find('div', {"class": "tagList"})
        tags = []
        for tag in tags_div.findAll(href=re.compile('/es/temas/')):
            tags.append(tag.text.strip())

        # PUSE COL 10
        content = ""
        paragraphs = soup.find('div', {"class": "article-main-body"}).findAll('p')

        for paragraph in paragraphs:
            content += '\n' + paragraph.text.strip()

        content = content.strip()
        # clean relate links from content
        # for relatyed_link in content.findAll('div', {"section": "shortcodeRelatedLinks"}):
        #    related_link.extract()
        # clean any inpage videos from content
        # for video in content.findAll(class_=re.compile("video")):
        #    video.extract()
        # clean any inpage galleries from content
        # for gallery in content.findAll(class_=re.compile("gallery")):
        #    gallery.extract()
        # clean of any figures so the caption wont appear
        # for figure in content.findAll('figure'):
        #    figure.extract()
        # clean of twits in content
        # for twit in content.findAll(class_=re.compile("twitter")):
        #    twit.extract()

        # content = content.text
        # assert content.find('function()') == -1

        new_entry = self.create_news_entry(title=title, content=content,
                                           # tags=tags,
                                           tags=["tecnologia"],
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)
        return new_entry

if __name__ == "__main__":
    CNetEspParser().parse("https://www.cnet.com/es/noticias/draft-nfl-2019-tv-internet-estados-unidos-futbol-americano/#ftag=ESPdf5230a")
