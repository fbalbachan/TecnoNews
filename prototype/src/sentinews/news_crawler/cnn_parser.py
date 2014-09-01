#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import etree
from re import sub
from urllib import urlopen
from src.sentinews.news_entry import NewsEntry


class CNNParser:
    def parse(self, url):
        whole_text = ""

        html = urlopen(url).read()
        tree = etree.HTML(html)

        nodes = tree.xpath("//div[@class='cnnRightPost']")

        node = nodes[0]

        content = ''
        title = ''
        tags = []

        for child in node:
            if child.tag == "p":
                text = etree.tostringlist(child, encoding = "utf-8")[0]

                text = sub("</?p>", "", text)
                text = sub("(<br />)+", " ", text)
                text = text.strip()

                whole_text = whole_text + text + "\n"

        whole_text = whole_text.strip()
        
        return NewsEntry(title, content, tags, url)
\