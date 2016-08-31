#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urlparse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser

class ElleParser(GenericParser):
    def __init__(self):
        super(ElleParser, self).__init__()

    source = u"Elle"

    def parse(self, url):
        #url = "http://www.elle.es/moda/news/cara-delevingne-im-not-a-trophy"
        #url = "http://www.elle.es/elledeco/casas/casa-michael-jackson-las-vegas"
	#soup = BeautifulSoup(self.opener.read(url).decode('utf-8','ignore'), from_encoding='utf-8')
        soup = BeautifulSoup(self.opener.read(url).decode("utf-8", 'ignore'))

	for script in soup(["script", "style"]):
            script.extract()


        for image in soup.findAll('img'):
            image.extract()


        for p in soup.findAll('p',{"class":"firma"}):
            p.extract()

        title = soup.find('h1', {'class':'titulo'})
        title = title.text.strip()


        subtitle = soup.find('h2', {'class':'subtitulo'})

        content = ""

        if subtitle:
            content = subtitle.text.strip() + "."

        intro = soup.find('div', {'class':'entradilla'})
        if intro:
            if content == "":
                content += intro.text.strip()
            else:
                content += "\n" + intro.text.strip()

        paragraphs = soup.find('div',{'class':'galeria'})

        if paragraphs is None:
            paragraphs = soup.find(True, {'class':[ 'articulo']})
        paragraphs = paragraphs.findAll('p')

        #content = ""
        for paragraph in paragraphs:
            for a in paragraph.findAll("a") :
                a.extract()
            content += "\n" + paragraph.text.strip()

        content = content.strip()

        raw_categories = soup.find('div',{'id':'breadCrumbs'}).findAll('a')

        categories=[]

        if len(raw_categories) > 0:
            raw_categories.pop(0)

        for category in raw_categories:
            categories.append(category.text.strip())

        #tags = []
        tags = ["belleza"]
        categories=["belleza"]
        #return {"tags":tags, "content":content, "title":title}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
