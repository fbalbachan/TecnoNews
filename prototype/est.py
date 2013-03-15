#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, os, sys, copy
from itertools import *
from conf import *
from estructura import *

def estructuras_balanceadas(lista):
    w = 0
    out = []
    nivel = 0
    # set position for each word
    for x in lista:
        if x.startswith('+(') or x.startswith('('):
            w += 1
            out.append(x+'{%d'%w)
        else:
            out.append(x)
    lista = out
    # parse bracketed structures
    stack = []
    for i, x in enumerate(lista):
        if x.endswith(']') and stack:
            start = stack.pop()
            nivel -= 1
            yield (start, i, lista[start:i+1], nivel) # (principio, fin, estructura, nivel)
        elif x.endswith('_['):
            stack.append(i)
            nivel += 1

def sujeto_para(verb):
    match = re.findall(r'1S0|2S0|1P0|2P0|3S0|3SM|3SF|3PM|3PF|3P0', verb.tag, re.U)
    if match:
        (persona_forma, persona_genero, persona_numero) = personas[match[0]]
        e = Estructura((-1,-1, ['sn_[', '+(%s %s PP2CSN00 -){1' % (persona_forma, persona_forma), ']'], -1))
        e.genero = persona_genero
        e.numero = persona_numero
        return e
