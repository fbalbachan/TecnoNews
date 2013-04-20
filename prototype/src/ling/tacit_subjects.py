#!/usr/bin/python
# -*- coding: utf-8 -*-

tacit_subjects = {
    (0, 'singular', 'neutral') : None,

    (1, 'singular', 'neutral') : u'yo',

    (2, 'singular') : u'tú',

    (3, 'singular', 'neutral')   : u'él',
    (3, 'singular', 'masculine') : u'él',
    (3, 'singular', 'feminine')  : u'ella',

    (1, 'plural', 'neutral')   : u'nosotros',
    (1, 'plural', 'masculine') : u'nosotros',
    (1, 'plural', 'feminine')  : u'nosotras',

    (2, 'plural')   : u'ustedes',

    (3, 'plural', 'neutral')   : u'ellos',
    (3, 'plural', 'masculine') : u'ellos',
    (3, 'plural', 'feminine')  : u'ellas',
}

def tacit_subject_for(verb_msi):
    return tacit_subjects[(verb_msi['person'], verb_msi['number'])]