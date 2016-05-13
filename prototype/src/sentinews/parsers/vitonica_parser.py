#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser

class VitonicaParser(GenericParser):
    def __init__(self):
        super(VitonicaParser, self).__init__()

    source = u"Vitonica"

    def parse(self, url):
        #url = "http://www.vitonica.com/dietas/el-indice-glucemico-de-un-alimento-podria-variar-de-una-persona-a-otra?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Vitonica+%28Vitonica%29"

	soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
	for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()


        title = soup.find('h1')
        title =  title.text.strip()


        content = ""
        content = soup.find('div',{'class':'article-content'}).find('div',{'class':'blob'}).text.strip()
        content = content.strip()

        topic_list = soup.find('div',{'class':'article-topics-list'})

        if topic_list != None:
            categories = []
            raw_categories = topic_list.find('ul',{'class':'article-topics-categories'})
            if raw_categories != None:
                raw_categories = raw_categories.findAll('a')
                for category in raw_categories:
                    categories.append(category.text.strip())

            tags = []
            raw_tags = topic_list.find('ul',{'class':'article-topics-tags'})
            if raw_tags != None:
                raw_tags = raw_tags.findAll('a')
                for tag in raw_tags:
                    tags.append(tag.text.strip())

        tags = ["salud"]
        categories=["salud"]

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
