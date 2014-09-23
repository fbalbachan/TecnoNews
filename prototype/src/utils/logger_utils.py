#!/usr/bin/env python
#-*- coding: utf-8 -*-
import logging

log_obj = None
def get_logger(file):
    global log_obj
    if not log_obj:
        logger    = logging.getLogger(file)
        logger.propagate = False
        handler   = logging.FileHandler('logs/'+file+'.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        log_obj = logger
    return log_obj
