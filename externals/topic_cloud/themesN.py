#!/usr/bin/env python
#-*- coding:utf-8 -*-
import nltk, codecs, re, operator, math, itertools
#from itertools import izip_longest
from utils.utils import sentence_delimiters
from utils.csvwrapper import *

import os
import sys
#import PyCUE

#from java.util import *
#from textprocessing.parser import Parser
#from textprocessing.interpreter import RequestContextEntry
#from textprocessing.language import LanguagesDistribution
#from textprocessing.ontology import Ontology
#from textprocessing.ontology.repository import OntologyRepository
#from cue.model import *
#from cue.model.specification import *


#cue = PyCUE.PyCUE('EN') # ES EN PT TODOS

#def u_raw_input(text):
#        return text.replace("á","\xe1").replace("é","\xe9").replace("í","\xed").replace("ó","\xf3").replace("ú","\xfa").replace("Á","\xc1").replace("É","\xc9").replace("Í","\xcd").replace("Ó","\xd3").replace("Ú","\xda").replace("ñ","\xf1").replace("Ñ","\xd1").replace("ç","\xe7").replace("Ç","\xc7").replace("¿","\xbf").replace("¡","\xa1").replace("ü","\xfc").replace("Ü","\xdc")

import json
from pymongo import MongoClient
from sys import argv
import bson

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bson.ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

mongo_data = {
    "host"  :   "85.10.210.172",
    "port"  :   27017,
    "db"    :   "sentinews_entrebit",
    "username" : "root",
    "password" : "NaturalezaMuerta"
}


def sentences(text):
    return filter(lambda x: x != None and x != '', [s.strip() if s != None else s for s in re.split(sentence_delimiters, text, re.U|re.I)])

def words(text):
    return [w.lower() for w in re.findall(r'\w+|\w-\w|^(?!http)\w+', text, re.U)]

def valid_token(w):
    if not(w.lower() in stopwords) and not(re.match(r'\d+|http|www', w, re.U)):
        return True
    else:
        return False

def contains_verb(token_tuple):
    for token in token_tuple:
        #if token.lower() in verbos:
        #    return True
        return True
    return False

# def grouper(n, iterable, padvalue=None):
#     "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
#     return izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)


#corpus_words = [w for opinion in opinions for w in re.findall(r'\w+|\w-\w', opinion[3], re.U|re.I)]

def themesN(n, freq_filter=4):
    def pmi(ngram, d1, dn):
        n = len(ngram)
        p_marginals = [d1[i] / float(d1.N()) for i in ngram]
        p_joint = dn[ngram]
        if 0 not in p_marginals:
            return abs(math.log(p_joint, 2) - math.log(reduce(lambda x,y: x*y, p_marginals, 1), 2))
        else:
            return 0

    # caso especial: unigramas
    if n == 1:
        freqs1 = nltk.probability.FreqDist(corpus_words_no_stopwords)
        useful_ngrams = filter(lambda (t, f): f >= freq_filter and valid_token(t[0]) , freqs1.items())
        return [((t,),f,0) for (t,f) in useful_ngrams]



    #ngrams = nltk.util.ngrams(corpus_words, n)
    ngrams = []
    for sentence in corpus_sentences:
        ngrams += filter(lambda x: x != [], nltk.util.ngrams(words(sentence), n))
    freqsN = nltk.probability.FreqDist(ngrams)
    # caso especial: bigramas no incluyen stopwords; el resto sí
    if n <= 2:
        freqs1 = nltk.probability.FreqDist(corpus_words_no_stopwords)
    else:
        freqs1 = nltk.probability.FreqDist(corpus_words)
    useful_ngrams = filter(lambda (t, f): f >= freq_filter
                           and valid_token(t[0])
                           and valid_token(t[len(t)-1])
                           and (contains_verb(t)),
                           freqsN.items())


    mi = [pmi(t,freqs1,freqsN) for (t, f) in useful_ngrams]
    out = sorted([(t,f,pmi_value) for ((t,f), pmi_value) in zip(useful_ngrams, mi)], key=operator.itemgetter(1), reverse=True)
    return out



def showNthemes(ngrams=2, howmany=10):
    for i, theme in enumerate(themesN(ngrams, freq_filter=freq_threshold_per_ngram[n])[:howmany_threshold_per_ngram[n]]):
        ngram, f, pmi_value = theme
        output = '%d,"%s",%d,%.2f' % (i+1, ' '.join(ngram), f, pmi_value)
        print output.encode('utf-8')
    print

def show(themes, howmany=10, return_sorted=False):
    for i, theme in enumerate(themes[:howmany]):
        ngram, f, pmi_value = theme
        output = '%d,"%s",%d,%.2f' % (i+1, ' '.join(ngram), f, pmi_value)
        print output.encode('utf-8')
    print

def get_themes(return_sorted=False):
    temas_candidatos = list(itertools.chain.from_iterable([themesN(n, freq_threshold_per_ngram[n])[:howmany_threshold_per_ngram[n]]
                                                      for n in range(1,9)]))
    #print "temas candidatos"
    #print temas_candidatos
    textos_candidatos = [' '.join(tema[0]) for tema in temas_candidatos]

    #print "textos candidatos"
    #print textos_candidatos

    temas_finales = [tema for tema in temas_candidatos if all(' '.join(tema[0]) not in tt for tt in textos_candidatos[textos_candidatos.index(' '.join(tema[0]))+1:])]

    #print "temas finales"
    #print temas_finales

    if return_sorted:
        return sorted(temas_finales, key=operator.itemgetter(1), reverse=True)
    else:
        return temas_finales


if __name__ == "__main__":
    # for n in range(7,0,-1): showNthemes(n)

    import sys
    language=sys.argv[1]
    if language=='pt':
        stopwords_file = 'stopwords.pt.txt'
        verbs_file = 'verbos.pt.txt'
    elif language=='en':
        stopwords_file = 'stopwords.en_empty.txt'
        verbs_file = 'verbos.en.txt'
    elif language=='es':
        stopwords_file = 'stopwords_es_limpios_sinNO.txt'
        verbs_file = 'verbos.es.txt'
    stopwords=set([w.strip().lower() for w in codecs.open(stopwords_file, 'r', 'utf-8').read().split()])
    verbos = set([w.strip().lower() for w in codecs.open(verbs_file, 'r', 'utf-8').read().split()])

    try:
        #se espera que sea un string tipo "2342362323,34535645,2346456456,"
        ids=sys.argv[2].split(",")
        client = MongoClient(mongo_data["host"], mongo_data["port"])

        if "username" in mongo_data :
            client["admin"].authenticate( mongo_data["username"], mongo_data["password"])

        db = client[mongo_data["db"]]
        oids = []
        for i in ids :
            oids.append(bson.ObjectId(i))

        #print oids
        items = db["news_entries"].find({"_id" : {"$in" : oids }})
        #print items
    except Exception, e:
        print sys.argv[2]
        print "Debe especificar uno o mas IDs de noticias. Imposible continuar."
        print str(e)
        sys.exit(1)

    #text_file = 'input.txt' #'BazaarBoys.csv' #'data/embelleze_30-10_30-11.csv'
    #text_reader = unicode_csv_reader(codecs.open(text_file, 'r', 'utf-8'), first_line_is_header=True)
    #opinions = [opinion for opinion in text_reader]

    opinions = []
    for i in items:
        opinions.append( i["title"] )
        opinions.append( i["content"] )

    #print opinions

    opinions_n = len(opinions)


    corpus_sentences = list(itertools.chain.from_iterable([sentences(opinion[0]) for opinion in opinions]))
    corpus_words = list(itertools.chain.from_iterable([words(s) for s in corpus_sentences]))
    corpus_words_no_stopwords = filter(lambda x: x not in stopwords, corpus_words)

    #if opinions_n < 100:
    freq_threshold_per_ngram = {1:8, 2:5, 3:3, 4:3, 5:3, 6:2, 7:2, 8:2}
    howmany_threshold_per_ngram = {1:10, 2:30, 3:20, 4:20, 5:10, 6:10, 7:5, 8:5}
    #elif opinions >= 100 and opinions <= 50000:
    #freq_threshold_per_ngram = {1:0.014, 2:0.01, 3:0.007, 4:0.007, 5:0.0017, 6:0.0017, 7:0.0017, 8:0.0017}
    #howmany_threshold_per_ngram = {1:0.01, 2:0.007, 3:0.003, 4:0.003, 5:0.0017, 6:0.0017, 7:0.0017, 8:0.0017}
    #for (k,v) in freq_threshold_per_ngram.iteritems():
        #freq_threshold_per_ngram[k] = int(round(v * opinions_n))
    #for (k,v) in howmany_threshold_per_ngram.iteritems():
        #howmany_threshold_per_ngram[k] = int(round(v * opinions_n))
    #else:
    #freq_threshold_per_ngram = {1:700, 2:500, 3:350, 4:350, 5:85, 6:85, 7:85, 8:85}
    #howmany_threshold_per_ngram = {1:30, 2:20, 3:10, 4:10, 5:5, 6:5, 7:5, 8:5}

    CSS_SIZES = range(1, 9)
    themes = get_themes(return_sorted=False)
    tags = dict([(' '.join(ngram), freq) for (ngram, freq, pmi_value) in themes])
    if len(tags) > 0:
        MAX = max(tags.values())
        STEP = MAX / float(len(CSS_SIZES))

    '''
    print """<!doctype html><html>"""
    print """<head><meta content="text/html; charset=utf-8" http-equiv="content-type"/>"""
    print """<style type="text/css">
      span.size-1 { font-size: 120%; }
      span.size-2 { font-size: 140%; }
      span.size-3 { font-size: 160%; }
      span.size-4 { font-size: 180%; }
      span.size-5 { font-size: 200%; }
      span.size-6 { font-size: 220%; }
      span.size-7 { font-size: 240%; }
      span.size-8 { font-size: 260%; }
    </style>"""
    print """<body>"""
    for tag, count in tags.items():
        tag = tag.encode('utf-8')
        css = int(round(count / STEP))
        print """<span class='size-%s'>%s, %d veces</span><br>""" % (css, tag, count),
    print "</body></html>"
    '''
    #show(themes, howmany=30, return_sorted=True)
    print "["
    for tag, count in tags.items():
        tag = tag.encode('utf-8')
        css = int(round(count / STEP))
        print "[\"" + tag + "\"," + str(count) + "],"
    print "[]]"
