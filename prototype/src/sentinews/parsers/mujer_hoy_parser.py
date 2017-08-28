#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser


class MujerHoyParser(GenericParser):
    def __init__(self):
        super(MujerHoyParser, self).__init__()

    source = u"MujerHoy"

    def parse(self, url):
        # url = "http://blogs.mujerhoy.com/maquillaje-estrellas/2016/08/04/maquillaje-ojos-de-gata-los-trucos-para-conseguir-el-perfecto-eyeliner.html"
        # url = "http://blogs.mujerhoy.com/adelgazar/2016/01/11/culos-sentados-grasas-en-expansion.html"
        # url = "http://www.mujerhoy.com/celebrities/corazon/201606/07/entrevista-noriega-michelle-jenner-amor-letra-20160607124020.html"
        if u"/galerias/" in url:
            return None
        soup = BeautifulSoup(self.opener.read(url).decode('utf-8', 'ignore'), "html.parser", from_encoding='utf-8')
        for script in soup(["script", "style"]):
            script.extract()

        for image in soup.findAll('img'):
            image.extract()

        title = soup.find('h1', {'itemprop': 'headline'})
        if title is None:
            title = soup.find('h1', {'class': 'headline'})
        title = title.text.strip()

        content = ""

        intro = soup.find('ul', {'class': 'descripcion-temas-pagina-final'})
        if intro:
            content = intro.text.strip()

        # This site has two templates. Gotta catch them all.
        article = soup.find('div', {'itemprop': 'articleBody'})
        if article is None:
            article = soup.find("div", {"class": ["description", "content"]})
        paragraphs = article.find_all("p")

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()

            content += "\n" + clean_text

        content = content.strip()

        tags = ["belleza"]
        categories = ["belleza"]
        # return {"content":content, "title":title}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
