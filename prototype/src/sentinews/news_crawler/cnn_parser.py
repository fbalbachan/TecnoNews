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
        content = top.find('div').text
        tags = top.find('span', class_ = "cnnBlogFiledBy cnn_categories").text[11:].split(u"\xa0\u2022\xa0")

        return NewsEntry(title, content, tags, u"CNN en español")
