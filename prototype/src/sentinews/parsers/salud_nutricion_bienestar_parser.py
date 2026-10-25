#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class SaludNutricionBienestarParser(GenericParser):
    def __init__(self):
        super(SaludNutricionBienestarParser, self).__init__()

    source = "Salud Nutrición Bienestar"

    def parse(self, url):
        #url = "http://www.saludnutricionbienestar.com/estrategias-reducir-riesgo-cancer/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+saludnutricionbienestar+%28Salud+Nutrici%C3%B3n+Bienestar%29&utm_content=FeedBurner"

        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()

        #-------------------TITLE--------------------------
        title = soup.find(True,{'class':'entry-title'})
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        article_content = soup.find(True,{'class':['entry-content', 'post-content']})

        paragraphs = article_content.findAll(['p','h2', 'li'])

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            if paragraph.name == "li":
                clean_text = "\t-" + clean_text
            content += "\n" + clean_text

        categories = ["salud"]
        tags = ["salud"]
        
        #categories=[urlparse(url).path.split("/")[1]]
        #print categories

        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
