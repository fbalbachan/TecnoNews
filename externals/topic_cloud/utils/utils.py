#!/usr/bin/env python
#-*- coding: utf-8 -*-

def quote(s, enc=True):
    if enc:
        return ('"%s"' % s).encode('utf-8')
    else:
        return '"%s"' % s

import re
sentence_delimiters = re.compile(r"""\.|[¿!¡;]+|(\?)+|\.\.\.\|""", re.U)
