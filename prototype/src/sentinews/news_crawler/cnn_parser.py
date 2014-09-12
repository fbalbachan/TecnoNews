#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry
from bs4 import BeautifulSoup


class CNNParser:
    def parse(self, url):
        soup = BeautifulSoup(urlopen(url).read())
        top = soup.findAll('div' , { "class" : "cnnRightPost" })[0]

        title = top.find('h1').text
        content_text = top.find('div').text

        content1 = content_text.split(u"\u2014")
        content2 = content_text.split(u"\u2013")
        
        if len(content1[0]) < len(content2[0]):
            content = "-".join(content1[1:])
        else:
            if len(content2) > 1:
                content = "-".join(content2[1:])
            else:
                content = content2[0]

        tags = top.find('span', class_ = "cnnBlogFiledBy cnn_categories").text[11:].split(u"\xa0\u2022\xa0")

        return NewsEntry(title, content, tags, u"CNN en español")
