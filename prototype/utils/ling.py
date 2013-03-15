#!/usr/bin/python
# -*- coding: utf-8 -*-

encabezadores = {
    u'cuánto': u'CANTIDAD',         
    u'cuántos': u'CANTIDAD',         
    u'cuánta': u'CANTIDAD',         
    u'cuántas': u'CANTIDAD',         
    u'quién': u'PERSONA',   
    u'quiénes': u'PERSONA',   
    u'cómo': u'MANERA',
    u'cuándo': u'TIEMPO',
    u'dónde': u'LUGAR',
    u'qué': u'INESPECÍFICO_QUE',
    u'cuál': u'INESPECÍFICO_CUAL',
    u'cuáles': u'INESPECÍFICO_CUAL',
    }

encabezadores_no_acentuados = {
    u'cuanto': u'CANTIDAD',         
    u'cuantos': u'CANTIDAD',         
    u'cuanta': u'CANTIDAD',         
    u'cuantas': u'CANTIDAD',         
    u'quien': u'PERSONA',   
    u'quienes': u'PERSONA',   
    u'como': u'MANERA',
    u'cuando': u'TIEMPO',
    u'donde': u'LUGAR',
    u'que': u'INESPECÍFICO_QUE',
    u'cual': u'INESPECÍFICO_CUAL',
    u'cuales': u'INESPECÍFICO_CUAL',
    }

encabezadores_todos = encabezadores.keys().extend(encabezadores_no_acentuados.keys())

antecesoras_cual = [
    u'tal',
    u'cada',
    u'la',
    u'las',
    u'el',
    u'los',
    u'lo',
    ]

antecesoras_que = [
    u'a',
    u'tal',
    u'con',
    u'de',
    u'en',
    u'desde',
    u'entre',
    u'hasta',
    u'para',
    u'por',
    u'sin',
    u'tras',
    u'ya',
    u'antes',
    u'después',
    u'despues',
    u'siempre',
    u'decir',
    u'afirmar',
    u'comentar',
    u'sugerir',
    u'gustar',
    u'encantar',
    u'odiar',
    u'creer',
    u'el',
    u'la',
    u'las',
    u'lo',
    u'los',
    u'más',
    u'mas',
    u'menos',
    u'igual',
    u'puesto',
    u'tanto',
    u'así',
    u'asi',
    ]

class EncabezadorMultipalabra(object):
    def __init__(self, encabezador, sucesora, category):
        self.encabezador = encabezador
        self.sucesora = sucesora
        self.category = category

encabezadores_multipalabra = [
    EncabezadorMultipalabra(u'cual', u'demora', u'TIEMPO'),
    EncabezadorMultipalabra(u'cual', u'demorar', u'TIEMPO'),
    EncabezadorMultipalabra(u'cual', u'dia', u'TIEMPO'),
    EncabezadorMultipalabra(u'cual', u'lugar', u'LUGAR'),
    EncabezadorMultipalabra(u'cual', u'momento', u'TIEMPO'),
    EncabezadorMultipalabra(u'cual', u'precio', u'CANTIDAD'), 
    EncabezadorMultipalabra(u'cual', u'zona', u'LUGAR'),
    EncabezadorMultipalabra(u'cual', u'costo', u'CANTIDAD'),
    EncabezadorMultipalabra(u'que', u'costo', u'CANTIDAD'),
    EncabezadorMultipalabra(u'cuanto', u'demora', u'TIEMPO'),
    EncabezadorMultipalabra(u'cuanto', u'demorar', u'TIEMPO'),
    EncabezadorMultipalabra(u'cuanto', u'tardar', u'TIEMPO'),
    EncabezadorMultipalabra(u'cuanto', u'tiempo', u'TIEMPO'),
    EncabezadorMultipalabra(u'que', u'demora', u'TIEMPO'),
    EncabezadorMultipalabra(u'que', u'demorar', u'TIEMPO'),
    EncabezadorMultipalabra(u'que', u'dia', u'TIEMPO'),
    EncabezadorMultipalabra(u'que', u'lugar', u'LUGAR'),
    EncabezadorMultipalabra(u'que', u'momento', u'TIEMPO'),
    EncabezadorMultipalabra(u'que', u'precio', u'CANTIDAD'),
    EncabezadorMultipalabra(u'que', u'salir', u'CANTIDAD'),
    EncabezadorMultipalabra(u'que', u'zona', u'LUGAR'),
    ]

verbos_actitud_interrogativa = [
    u'saber', u'informar', u'decir', u'conocer', u'preguntar', u'responder', u'confirmar', u'consultar',
    ]

verbos_equivalentes = {
    u'salir' : u'valer',
    u'valer' : u'valer',
    
    u'contactar' : u'llamar',
    u'llamar' : u'llamar',
    
    u'ubicar' : u'vivir',
    u'vivir' : u'vivir',
    
    u'dar' : u'ofrecer',
    u'ofrecer' : u'ofrecer',
    
    u'adquirir' : u'comprar',
    u'comprar' : u'comprar',
    
    u'contar' : u'tener',
    u'tener' : u'tener',

    u'realizar' : u'hacer',
    u'hacer' : u'hacer',

    u'abonar' : u'pagar',
    u'pagar' : u'pagar',

    u'ofertar' : u'comprar',
    u'comprar' : u'comprar',

    u'mandar' : u'enviar',
    u'enviar' : u'enviar',
    u'entregar' : u'enviar',
    u'llevar' : u'enviar',

    u'demorar' : u'tardar',
    u'tardar' : u'tardar',

    u'salir' : u'costar',
    u'cobrar' : u'costar',
    u'valer' : u'costar',
    u'costar' : u'costar',

    u'utilizar' : u'usar',
    u'usar' : u'usar',

    u'ocurrir' : u'pasar',
    u'pasar' : u'pasar',

    u'ver' : u'mirar',
    u'mirar' : u'mirar',
    
    }

#donde, como, que, cual, cuales indice debe ser <= 4, empezando de 0

personas_equivalentes = {
    u'usted' : u'vos',
    u'ud.' : u'vos',
    u'uds.' : u'vos',
    u'ud' : u'vos',
    u'uds' : u'vos',
    u'vosotros' : u'vos',
    u'vosotras' : u'vos',
    u'ustedes' : u'vos',
    u'tú' : u'vos',
    u'vos' : u'vos',
    u'nosotros' : u'yo',
    u'nosotras' : u'yo',
    u'yo' : u'yo',
    }
