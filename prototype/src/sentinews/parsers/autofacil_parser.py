#!/usr/bin/python
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re

class AutoFacilParser(GenericParser):
    def __init__(self):
        super(AutoFacilParser, self).__init__()

    source = "Auto Facil"

    def parse(self, url):
        #url = "http://www.autofacil.es/mecanica/2016/03/28/coches-rompen-mercado/31405.html"
        #url = "http://www.autofacil.es/radares-multas/2016/04/06/instalan-radar-solidario-cantabria/31601.html"
        #url = "http://www.autofacil.es/conductor/2016/04/06/gana-curso-derrape-porsche-handling-experience-gratis-autofacil/31591.html"
        soup = BeautifulSoup(self.opener.read(url),"html.parser" , from_encoding='windows-1252')
        for script in soup(["script", "style"]):
            script.extract()

        #-------------------TITLE--------------------------
        title = soup.find(True,{'itemprop':'headline'})
        title = title.text.strip()

        #-------------------CONTENT--------------------------
        content = ""

        #intro = soup.find('h3')

        #if intro is not None:
        #    content = intro.text.strip() + "\n"


        article_content = soup.find(True,{'itemprop':'articleBody'})

        paragraphs = article_content.findAll(['p','h3'])

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text

        categories = ["automóviles"]
        tags = ["automóviles"]

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
