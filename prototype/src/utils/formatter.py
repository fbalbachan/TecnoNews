#!/usr/bin/env python
#-*- coding: utf-8 -*-
from .logger_utils import *

logger = get_logger('entinews')

def logged_entities(entities):
    sorted_entities = sorted(entities) #, key=lambda e: e.estructura.__str__())
    logger.info('.'*80); logger.info("sorted entities: %s" % ' - '.join([e.__str__() for e in sorted_entities]))
    return sorted_entities

def logged_subject(subject):
    logger.info('.'*80); logger.info("subject: %s | %s" % (subject, subject.msi))
    return subject