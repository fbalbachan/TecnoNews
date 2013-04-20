#!/usr/bin/python
# -*- coding: utf-8 -*-

tacit_subjects = {
    (0, 'singular') : None,
    (1, 'singular') : u'yo',
    (2, 'singular') : u'tú',
    (3, 'singular') : u'él',
    (1, 'plural') : u'nosotros',
    (2, 'plural') : u'ustedes',
    (3, 'plural') : u'ellos',
}

def tacit_subject_for(verb_msi):
    return tacit_subjects[(verb_msi['person'], verb_msi['number'])]