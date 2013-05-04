#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils.logger_utils import *

class Boxes(object):

    def __init__(self, subject=None, verb=None, XXX=None, adjunct=None):
        self.logger = get_logger('entinews')

        self.subject = subject
        self.verb    = verb
        self.XXX     = XXX
        self.adjunct = adjunct

        self.od       = None
        self.oi       = None
        self.regimen  = None
        self.equative = None

    def __str__(self):
        return ' '.join([u"[ %s ]" for box in [self.subject, self.verb, self.XXX, self.adjunct]])