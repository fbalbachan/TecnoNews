#!/usr/bin/python
# -*- coding: utf-8 -*-

class Palabra(object):
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
        self.genero = None
        self.numero = None
        self.sentiment = (0, 0)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '%s' % (self.form)

