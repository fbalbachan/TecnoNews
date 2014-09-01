# -*- coding: utf-8 -*-

'''Struct class to contain the news information'''
class NewsEntry(object):
    def __init__(self, title, content, tags, source):
        self.title = title
        self.content = content
        self.tags = tags
        self.source = source