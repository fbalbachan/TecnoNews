#!/usr/bin/python
# -*- coding: utf-8 -*-
from model.structure import build_structure

tacit_subjects = {
    (0, 'singular', 'neutral') : None,

    (1, 'singular', 'neutral') : u'yo',

    (2, 'singular', 'neutral') : u'tú',

    (3, 'invariable', 'neutral') : u'lo',
    (3, 'singular', 'neutral')   : u'él',
    (3, 'singular', 'masculine') : u'él',
    (3, 'singular', 'feminine')  : u'ella',

    (1, 'plural', 'neutral')   : u'nosotros',
    (1, 'plural', 'masculine') : u'nosotros',
    (1, 'plural', 'feminine')  : u'nosotras',

    (2, 'plural', 'neutral')   : u'ustedes',

    (3, 'plural', 'neutral')   : u'ellos',
    (3, 'plural', 'masculine') : u'ellos',
    (3, 'plural', 'feminine')  : u'ellas',
}

def tacit_subject_for_passive_sentence():
    subject = build_structure(word=u'alguien')
    subject.msi = (3, 'singular', 'neutral')
    return subject 

def tacit_subject_for(verb):
    return tacit_subjects[(verb.msi['person'], verb.msi['number'], verb.msi['gender'])]

