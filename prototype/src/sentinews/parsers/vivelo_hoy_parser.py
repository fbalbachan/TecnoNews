#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from src.sentinews.parsers.generic_parser import GenericParser


class ViveloHoyParser(GenericParser):
    def __init__(self):
        super(ViveloHoyParser, self).__init__()

    source = "Vivelo Hoy"

    def is_parseable(self, url, soup=None):

        allowed = True
        if not soup:
            soup = BeautifulSoup(self.opener.read(url))

        if "/video/" in url:
            allowed = False
        #lso post de opinion no van
        category = soup.find('meta',{"property":"article:section"})
        if ('Opinión' in category['content']) or ('Entretenimiento' in category['content']):
            allowed = False
        #los post sin tags son solo video
        tag_list = soup.findAll('meta',{"property":"article:tag"})
        if not tag_list:
            allowed = False

        #take out post that are photo galleries
        gallery = soup.findAll(class_=re.compile("format-post-format-gallery"))
        if gallery:
             allowed = False

        return allowed

    def parse(self, url):

        soup = BeautifulSoup(self.opener.read(url))

        if not self.is_parseable(url=url, soup=soup):
            return None

        # rip out script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        for embed in soup.find("iframe", {"class": "wp-embedded-content"}):
            embed.extract()

        image_search_string = None

        title = soup.find('h1', {"class": ["entry-title", "detailTitle"]})
        title = title.text

        category = soup.find('meta',{"property":"article:section"})
        categories=[category['content']]

        content = soup.find('div', {"class" : "entry-content"})

        figures = content.findAll('figure')
        for figure in figures:
            figure.extract()

        #taking out videos
        videos = content.findAll('div', {"class":"outer-container"})
        for video in videos:
            video.extract()

        twits = content.findAll(class_=re.compile("twitter"))
        for twit in twits:
            twit.extract()

        sides = content.findAll(True,{"class": ["col-side", "footerDetail"]})
        for side in sides:
            side.extract()


        #remove city names

        tag_list = soup.findAll('meta',{"property":"article:tag"})
        tags = []
        for tag in tag_list:
            tags.append(tag['content'])

        paragraphs =  content.findAll('p')
        if paragraphs:
            last_paragraph = paragraphs.pop()
            if re.match('[_|-| ]?Por .+',last_paragraph.text):
                last_paragraph.extract()

        content = content.text
        #remove certain strings
        content = re.sub('-Con servicios de w+','',content)
        content = re.sub(r'– ?Con información .+', '', content)
        content = re.sub('EFE[USA]*', '',content)
        content = re.sub('—Agencias', '',content)
        #take out first line
        first_line_regex = re.compile(r'( ?\S)+? ?[-|—|–]')
        content = first_line_regex.sub('', content, 1)
        content = content.strip()

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=image_search_string,
                                           keywords=None)

        return new_entry
