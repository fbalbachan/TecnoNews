#!/usr/bin/env python
#-*- coding: utf-8 -*-
from logger_utils import *

def format_entities(entities):
    logger = get_logger('sentilecto')

    sorted_entities = sorted(entities) #, key=lambda e: e.estructura.__str__())
    logger.info('.'*80); logger.info("sorted entities: %s" % ' - '.join([e.__str__() for e in sorted_entities]))

    return sorted_entities
