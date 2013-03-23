#!/usr/bin/python
# -*- coding: utf-8 -*-

class GlobalOperator(object):
    def __init__(self, (form, category, value)):
        self.form = form
        self.category = category
        self.value = value
        
    def __str__(self):
        if self.category:
            output = "(%s %s %d)" % (self.form, self.category, self.value)
        else:
            return "x"