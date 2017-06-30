#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re #, unidecode

token_regex = re.compile(r'\w+|\w+\'\w+|[\w$]+', re.U|re.I)
question_regex = re.compile(ur"""[.,¿]?([_\-$\w\s]+)\?+""", re.U|re.I)

#repeat_regex = re.compile(r'([abdefghijkmnñopqstuvwxyzABDEFGHIJKMNÑOPQSTUVWXYZáéíóúÁÉÍÓÚ])\1+')
repeat_regex = re.compile(r'([abdefghijkmnñopqstuvwxyzABDEFGHIJKMNÑOPQSTUVWXYZáéíóúÁÉÍÓÚ])\1\1+')
#replacement = r'\1\1'
replacement = r'\1'


def detroll(text):

    def por_token(p_token):
        p_token = p_token.decode("utf-8")
        if not all_in_upper_case(p_token) \
           and (not first_in_upper_case(p_token) or not all_rest_in_lower_case(p_token)):
            p_token = p_token.lower()
        return p_token.encode("utf-8")

    #output_tokens = [por_token(token) for token in text.split()]
    output_tokens = text.split()
    for index, token in enumerate(output_tokens):
        there_is_next_token = index < len(output_tokens)-1
        if there_is_next_token:
            token = output_tokens[index]
            next_token = output_tokens[index+1]
            if len(token) >2 and all_in_upper_case(token) and all_in_upper_case(next_token):
                #return text.lower()
                current_index = index
                while current_index < len(output_tokens) and all_in_upper_case(output_tokens[current_index]):
                    output_tokens[current_index] = output_tokens[current_index].lower()
                    current_index += 1

    return ' '.join(output_tokens)


def first_in_upper_case(token):
    return token[0].upper() == token[0]


def all_rest_in_lower_case(token):
    return token[1:].lower() == token[1:]


def all_in_upper_case(token):
    return re.match(r"[abdefghijkmnñopqstuvwxyzABDEFGHIJKMNÑOPQSTUVWXYZáéíóúÁÉÍÓÚ]", token) and token.upper() == token


def limpieza_inicial(s):
    # estos replaces están porque Freeling reemplaza estos signos (si están solos) por 'y'
    s = s.replace('&', 'y')
    #s = s.replace('¡', '')
    #s = s.replace('-', '')
    #s = s.replace('–', '')
    #s = s.replace('¿', '')
    #s = s.replace('"', '')
    #s = s.replace("'", '')
    #s = s.replace("“", '')
    #s = s.replace("”", '')
    #s = s.replace("»", '')
    #s = s.replace("«", '')
    #s = s.replace("˵", '')
    #s = s.replace("`", '')
    #s = s.replace("‘", '')
    #s = s.replace("˶", '')
    #s = s.replace("/", '')
    #s = s.replace("%", '')
    #s = s.replace("+", '')
    #s = s.replace("(", '')
    #s = s.replace(")", '')
    s = s.replace("#", '')
    s = s.replace("@", '')
    s = s.replace("_", ' ')
    #s = s.replace("=", '')
    #s = s.replace("º", '')
    #s = s.replace("ª", '')
    #s = s.replace(":", '.') # Se comenta para atrapar adecuadamente horas
    s = re.sub(r'\bq\b', 'que', s)
    s = re.sub(r'\bQ\b', 'que', s)
    s = re.sub(r'\bxq\b', 'porque', s)
    s = re.sub(r'\bXQ\b', 'porque', s)
    s = re.sub(r'\bRT\b', ':', s)
    #s = re.sub(r'\bx\b', 'por', s)
    #s = re.sub(r'\bX\b', 'por', s)
    #s = re.sub(r'\bd\b', 'de', s)
    s = re.sub(r'\?+', '?', s)
    s = re.sub(r'\!+', '!', s)
    s = re.sub(r'\b(http|HTTP)\:--\S*\b', '', s)
    s = re.sub(r'\biPhone\b', 'Iphone', s)
    # s = re.sub(r"\n+(\w)", '.\1', s, re.U)
    s = re.sub(r'([0-9]+([,.][0-9]+)?)%', r'%\1', s)
    return s


def replace_repeated_letters(token):
    return re.sub(repeat_regex, replacement, token)


def normalize_and_tokenize(text, regex=r'\w+'):
    return [w.lower() for w in re.findall(regex, text)]
