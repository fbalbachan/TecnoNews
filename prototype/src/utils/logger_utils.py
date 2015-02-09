#!/usr/bin/env python
#-*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler

log_obj = None
def get_logger(file):
    #make it a dict and use it to check for diferent files
    global log_obj
    if not log_obj:
        logger    = logging.getLogger(file)
        logger.propagate = False
        handler   = logging.FileHandler('logs/'+file+'.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        rotation_handler = RotatingFileHandler('logs/'+file+'.log',
            maxBytes=5000000, backupCount=10)
        logger.addHandler(handler)
        logger.addHandler(rotation_handler)
        logger.setLevel(logging.INFO)
        log_obj = logger
    return log_obj

crawler_logger = None
def get_crawler_logger():
    global crawler_logger
    if not crawler_logger:
        import logging
        from logging.handlers import RotatingFileHandler
        import logging.handlers

        logging.basicConfig(level=logging.INFO, format='%(message)s')

        logger = logging.getLogger('Crawler')
        logger.addHandler(RotatingFileHandler('logs/crawlers.log', 'a',
            maxBytes=5000000, backupCount=5))
        logger.addHandler(logging.StreamHandler())
        logger.propagate = False
        crawler_logger = logger
    return crawler_logger
