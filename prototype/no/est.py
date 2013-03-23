#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, os, sys, copy
from itertools import *
from conf import *
from structure import *

def sujeto_para(verb):
    match = re.findall(r'1S0|2S0|1P0|2P0|3S0|3SM|3SF|3PM|3PF|3P0', verb.tag, re.U)
    if match:
        (persona_forma, persona_genero, persona_numero) = personas[match[0]]
        e = Structure((-1,-1, ['sn_[', '+(%s %s PP2CSN00 -){1' % (persona_forma, persona_forma), ']'], -1))
        e.gender = persona_genero
        e.number = persona_numero
        return e
