#!/usr/bin/env python
#-*- coding: utf-8 -*-
import logging

def get_logger(file):
    logger    = logging.getLogger(file)
    handler   = logging.FileHandler('logs/'+file+'.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
