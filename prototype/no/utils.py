#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, os
from tokenize import *
from itertools import islice

def u(t): return t.encode('utf-8')

def take(n, iterable):
    """return first n items of the iterable as a list"""
    return list(islice(iterable, n))

def get_words_via_freeling(sentence):
    """return words, using freeling in <--outf parsed> mode"""
    token_list = re.findall(token_regex, sentence)
    if token_list and not(re.match(r'\(|\)|\[|\]\|\{|\}', sentence)):
        comando = """echo "%s ." | analyzer_client localhost 5555"""
        parsed_sentence = os.popen(comando % sentence.encode('utf-8')).read().strip()
        parsed_sentence = parsed_sentence.decode('utf-8')
        just_word_lines = filter(lambda s: s.strip().startswith('+(') or s.strip().startswith('('), parsed_sentence.split('\n'))
        if parsed_sentence:
            return [word_line.strip().strip('+(').strip('(').strip(' -)').split() for word_line in just_word_lines]
    else:
        return []
    
def uniquer(seq):
    def idfun(x): return x.position
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result
