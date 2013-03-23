#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re, unidecode

token_regex = re.compile(r'\w+|\w+\'\w+|[\w$]+', re.U|re.I)
# sentence_delimiters = re.compile(ur'\.\s+|\?\s+|:\s+|[!;,]+|\.\.\.', re.U) #(?<=\w|\s)
sentence_delimiters = re.compile(ur"""\?+|\n|\. |,pero|, pero|:\s+|, y|,y|,mientras|, mientras|,entonces|, entonces|, aunque|,aunque|, sin embargo|,sin embargo|, no obstante|,no obstante|!+|; |\.\.\.|, pues|,pues""", re.U|re.I)
question_regex = re.compile(ur"""[.,¿]?([_\-$\w\s]+)\?+""", re.U|re.I)

def detroll(text):
    def por_token(token):
        if token.upper() == token:
            return token.lower()
        else:
            return token
    return ' '.join([por_token(token) for token in text.split()])

def limpieza_inicial(s):
    # estos replaces están porque Freeling reemplaza estos signos (si están solos) por 'y'
    s = s.replace(u'¡', '', re.U)
    s = s.replace(u'!', '', re.U)
    s = s.replace(u'¿', '', re.U)
    s = s.replace(r'"', '', re.U)
    s = s.replace(r"'", '', re.U)
    s = s.replace(u"“", '', re.U)
    s = s.replace(u"»", '', re.U)
    s = s.replace(u"«", '', re.U)
    s = s.replace(u"˵", '', re.U)
    s = s.replace(u"`", '', re.U)
    s = s.replace(u"‘", '', re.U)
    s = s.replace(u"˶", '', re.U)
    s = s.replace(u"”", '', re.U)
    s = re.sub(r'\bq\b', u'que', s)
    s = re.sub(r'\bQ\b', u'que', s)
    s = re.sub(r'\?+', u'?', s)
    # s = re.sub(r"\n+(\w)", '.\1', s, re.U)
    return s

def replace_repeated_letters(token):
    replaced_token = re.sub(repeat_regex, replacement, token)
    if replaced_token != token:
        return replace_repeated_letters(replaced_token)
    else:
        return replaced_token

def normalize_and_tokenize(text, regex=r'\w+'):
    return [unidecode.unidecode(w).lower() for w in re.findall(regex, text)]
