#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, codecs

relativos = [u'que', u'quien', u'quienes', u'el cual', u'la cual', u'los cuales', u'las cuales', u'el que', u'la que', u'los que', u'las que'] # u'lo cual', 

pronombres_objeto = {
    ('1', 'C', 'S'): u'yo',
    ('1', 'C', 'P'): u'nosotros',
    ('2', 'C', 'S'): u'vos',
    ('2', 'C', 'P'): u'ustedes',
    ('3', 'C', 'S'): u'él',
    ('3', 'C', 'N'): u'él',
    ('3', 'F', 'S'): u'ella',
    ('3', 'C', 'P'): u'ellos',
    ('3', 'F', 'P'): u'ellas',
}

gen_num_relativos = {
    u'que':  ('*','*'),
    u'quien': ('*','S'),
    u'quienes': ('*','P'),
    u'el cual': ('M','S'),
    u'la cual': ('F','S'),
    #u'lo cual': ('*','S'),
    u'los cuales': ('M','P'),
    u'las cuales': ('F','P'),
}

formas_terceras = {
    u'él': ('él', 'M', 'S'),
    u'ella': ('ella', 'F', 'S'),
    u'ello': ('ello', '*', 'S'),
    u'éste': ('éste', 'M', 'S'),
    u'ésta': ('ésta', 'F', 'S'),
    u'ése': ('ése', 'M', 'S'),
    u'ésa': ('ésa', 'F', 'S'),
    u'aquél': ('aquél', 'M', 'S'),
    u'aquélla': ('aquélla', 'F', 'S'),

    # u'él/ella': ('él/ella', '*', 'S'),
    # u'ellos/ellas': ('ellos/ellas', '*', 'P'),
    u'ellos': ('ellos', 'M', 'P'),
    u'ellas': ('ellas', 'F', 'P'),
    u'éstos': ('éstos', 'M', 'P'),
    u'éstas': ('éstas', 'F', 'P'),
    u'ésos': ('ésos', 'M', 'P'),
    u'ésas': ('ésas', 'F', 'P'),
    u'aquéllos': ('aquéllos', 'M', 'P'),
    u'aquéllas': ('aquéllas', 'F', 'P'),
}

subjetivemas_data = [line.strip().split(',') for line in codecs.open('sentiwordnet.csv', 'r', 'utf-8-sig').readlines()]
subjetivemas = dict([(word, (int(pos), int(neg))) for (word, pos, neg) in subjetivemas_data])
scripts_verbales_data = [line.strip().split(',') for line in codecs.open('scripts_verbales.csv', 'r', 'utf-8').readlines()]
scripts_verbales = dict([(word, classif) for [word, classif] in scripts_verbales_data])
global_operators = []
for line in codecs.open('global_valence_shifters.txt', 'r', 'utf-8').readlines():
    a, b, c = line.strip().split(',')
    global_operators.append((a,b,int(c)))
global_operator_words = [go for (go, cat, value) in global_operators]

assert(subjetivemas[u'espléndido'] == (100, 0))
assert(subjetivemas[u'terrible'] == (0, 80))
assert(subjetivemas[u'maravilloso'] == (85, 0))
assert(scripts_verbales[u'abanderizar'] == u'N')

labels_de_sn = ['sn', 'grup-verb-inf', 'patons', 'ptonic']

labels_de_entidad = ['sn', 'grup-verb', 'subord-rel', 'subord']

labels_de_nucleo_de_grup_verb_inf = [
    ('forma-inf', '*', '*')
]

labels_de_nucleo_de_sn = [
# TODO: guardar sólo labels; atributos salen del mapeador de msi
('n-ms', 'M','S'),         
('n-mp', 'M','P'),         
('n-fs', 'F','S'),         
('n-fp', 'F','P'),         

('w-ms', 'M','S'),         
('w-fs', 'F','S'),         
('w-mp', 'M','P'),         
('w-fp', 'F','P'),         

('psubj-mp', 'M','P'),
('psubj-ms', 'M','S'),
('psubj-fs', 'F','S'),
('psubj-s', '*','S'),

('j-ms', 'M','S'),         
('j-mp', 'M','P'),         
('j-fs', 'F','S'),         
('j-fp', 'F','P'),         

('pdem-ms', 'M','S'),         
('pdem-mp', 'M','P'),         
('pdem-fs', 'F','S'),         
('pdem-fp', 'F','P'),         

('parti-ms', 'M','S'),         
('parti-mp', 'M','P'),         
('parti-fs', 'F','S'),         
('parti-fp', 'F','P'),         

('pindef-mp', 'M','P'),
('pindef-ms', 'M','S'),
('pindef-fs', 'F','S'),
('pindef-s', '*','S'),

('paton-s', '*','S'),
('paton-p', '*','P'),
]

personas = {
    '1S0': (u'yo', '*', 'S'),
    '2S0': (u'vos', '*', 'S'),
    '3S0': (u'él', 'M', 'S'),
    '1P0': (u'nosotros', 'M', 'P'),
    '2P0': (u'ustedes', 'M', 'P'),
    '3P0': (u'ellos', 'M', 'P'),
    }

tacitos = [u'él/ella', u'ellos/ellas']

marcas_negacion = [word.strip() for word in codecs.open('global_valence_shifters.txt', 'r', 'utf-8-sig').readlines()]

marca_pasiva = 'verb-pass'

labels_de_determinante = [u'espec-ms', u'espec-mp', u'espec-fs', u'espec-fp', u'numero-nopart']

preposiciones_para_subordinada_oblicua = [u'ante', u'bajo', u'cabe', u'con', u'contra', u'de', u'desde', u'durante', u'en', u'entre', u'hacia', u'hasta', u'mediante', u'para', u'por', u'según', u'sin', u'sobre', u'tras']