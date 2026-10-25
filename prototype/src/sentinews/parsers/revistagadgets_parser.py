#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from src.sentinews.parsers.generic_parser import GenericParser
import re
from src.utils.unicodeTools import safe_unicode

class RevistagadgetsParser(GenericParser):
    def __init__(self):
        super(RevistagadgetsParser, self).__init__()

    source = "revistagadgets"
    
    def parse(self, url):
        #url = "http://www.revistagadgets.com/www/2016/04/06/build-bear-mexico-cerro-positivamente-2015-2016-abrira-7-espacios-mas-pais/"
        
        soup = BeautifulSoup(self.opener.read(url), from_encoding='utf-8')
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
            
        for image in soup.findAll('img'):
            image.extract()
        
        
        title = soup.select('h1.entry-title')[0].text.strip()
        
        content = ""
        article_content = soup.select('div#content-area')[0]
        
        paragraphs = article_content.findAll('p')

        for paragraph in paragraphs:
            clean_text = paragraph.text.strip()
            content += "\n" + clean_text
        
        content = content.strip()
        

        tags        =   []
        categories  =   None #que decida desde los tags
        title       =   safe_unicode(title)
        content     =   safe_unicode(content)
        
        tmptags = soup.select("div.post-tags")[0].findAll("a")
        for t in tmptags :
            tags.append( safe_unicode( t.text.strip() ) )
        
        
        #return {"title":title, "content":content, "tags" : tags}
        new_entry = self.create_news_entry(title=title, content=content,
                                           tags=tags,
                                           source=self.source,
                                           url=url,
                                           original_categories=categories,
                                           image_search_string=None,
                                           keywords=None)

        return new_entry
