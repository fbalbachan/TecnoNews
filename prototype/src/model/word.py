#!/usr/bin/python
# -*- coding: utf-8 -*-

class Word(object):
    def __init__(self, content):
        try:
            content, position = content.strip('+(').strip('(').split('{')
            self.form, self.lemma, self.tag = content.strip(' -)').split()
            self.position = int(position)
        except ValueError:
            self.form = None
            self.lemma = None
            self.tag = None
            self.position = None
        self.gender = None
        self.number = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return u'[%s|%s|%s]' % (self.form, self.tag, self.position)