#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re #, unidecode

token_regex = re.compile(r'\w+|\w+\'\w+|[\w$]+', re.U|re.I)
question_regex = re.compile(ur"""[.,¿]?([_\-$\w\s]+)\?+""", re.U|re.I)

#repeat_regex = re.compile(r'([abdefghijkmnñopqstuvwxyzABDEFGHIJKMNÑOPQSTUVWXYZáéíóúÁÉÍÓÚ])\1+')
repeat_regex = re.compile(r'([abdefghijkmnñopqstuvwxyzABDEFGHIJKMNÑOPQSTUVWXYZáéíóúÁÉÍÓÚ])\1\1+')
#replacement = r'\1\1'
replacement = r'\1'

re.sub(r'([a-z])\1+', r'\1', 'ffffffbbbbbbbqqq')

def detroll(text):
    def por_token(index, token):
        token = token.decode("utf-8")
        if index == 0:
            token = token[0].upper() + token[1:].lower()
        elif not (token[0].upper() == token[0] and token[1:].lower() == token[1:]):
            token = token.lower()
        return token.encode("utf-8")
    return ' '.join([por_token(index, token) for index, token in enumerate(text.split())])

def limpieza_inicial(s):
    # estos replaces están porque Freeling reemplaza estos signos (si están solos) por 'y'
    s = s.replace('¡', '')
    #s = s.replace('!', '')
    s = s.replace('¿', '')
    s = s.replace('"', '')
    s = s.replace("'", '')
    s = s.replace("“", '')
    s = s.replace("»", '')
    s = s.replace("«", '')
    s = s.replace("˵", '')
    s = s.replace("`", '')
    s = s.replace("‘", '')
    s = s.replace("˶", '')
    s = s.replace("”", '')
    s = s.replace("/", '')
    s = re.sub(r'\bq\b', 'que', s)
    s = re.sub(r'\bQ\b', 'que', s)
    s = re.sub(r'\?+', '?', s)
    # s = re.sub(r"\n+(\w)", '.\1', s, re.U)
    return s

def replace_repeated_letters(token):
    return re.sub(repeat_regex, replacement, token)

def normalize_and_tokenize(text, regex=r'\w+'):
    return [w.lower() for w in re.findall(regex, text)]
