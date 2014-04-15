#!/usr/bin/python
# -*- coding: utf-8 -*-

tacit_subjects = {
    (0, 'singular', 'neutral') : None,

    (1, 'singular', 'neutral') : 'yo',

    (2, 'singular', 'neutral') : 'tú',

    (3, 'invariable', 'neutral') : 'lo',
    (3, 'singular', 'neutral')   : 'él',
    (3, 'singular', 'masculine') : 'él',
    (3, 'singular', 'feminine')  : 'ella',

    (1, 'plural', 'neutral')   : 'nosotros',
    (1, 'plural', 'masculine') : 'nosotros',
    (1, 'plural', 'feminine')  : 'nosotras',

    (2, 'plural', 'neutral')   : 'ustedes',

    (3, 'plural', 'neutral')   : 'ellos',
    (3, 'plural', 'masculine') : 'ellos',
    (3, 'plural', 'feminine')  : 'ellas',
}

def tacit_subject_for(verb):
    gender = verb.msi['gender']
    if not gender:
        gender = "neutral"
    return tacit_subjects[(verb.msi['person'], verb.msi['number'], gender)]