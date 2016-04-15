#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
__author__ = 'Fernando Balbachan'
import nltk
import re
import numpy
from src.utils.configProvider import ConfigProvider

class TextDistance(object):

    def __init__(self):
        self.valid_token_regex = re.compile(r'[áéíóúñäëïöüáàâéèêíìîóòôúùûãçêôõø]*(\w+)[áéíóúñäëïöüáàâéèêíìîóòôúùûãçêôõø]*(\w*)')
        self.tokenizer_custom = nltk.tokenize.RegexpTokenizer(self.valid_token_regex)
        self.stopwords = self.load_stopwords()

    def tokenize(self, text):
            return self.tokenizer_custom.tokenize(text.strip().lower())

    def pre_process(self, text):
        # Lower text and tokenize
        text = self.tokenizer_custom.tokenize(text.strip().lower())
        # Clean Stopwords (already lowered)
        text = [w for w in text if w not in self.stopwords]
        return text

    def load_stopwords(self):
        stopwords = []
        config = ConfigProvider()

        stopwords_filename = config.get("resources", "stopwords_es_clean")

        for line in open(stopwords_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                stopwords.append(self.safe_unicode(line.rstrip('\n')))

        return stopwords

    def safe_unicode(self, text):
        if isinstance(text, unicode):
            u_text = text
        else:
            try:
                u_text = unicode(text, 'utf-8', errors='ignore')
            except Exception, e:
                u_text = text

        return u_text

    @staticmethod
    def cosine(x, y):
        return nltk.cluster.cosine_distance(numpy.array(x),
                                        numpy.array(y))

    def title_distance(self, title1, title2):
        from nltk import jaccard_distance
        word_set1 = set(self.pre_process(title1))
        word_set2 = set(self.pre_process(title2))
        return jaccard_distance(word_set1, word_set2)

    def distance(self, text1, text2, n):
        #print "textDistance.distance:"
        tokens1, tokens2 = self.pre_process(text1), self.pre_process(text2)
        #print "tokens"
        #print [tokens1, tokens2]
        ngrams1, ngrams2 = nltk.ngrams(tokens1, n), nltk.ngrams(tokens2, n)
        #print "ngrams"
        #print [ngrams1, ngrams2]
        f1, f2 = nltk.FreqDist(ngrams1), nltk.FreqDist(ngrams2)
        #print "FreqDists"
        #print [f1,f2]
        dimensiones = set(ngrams1).union(set(ngrams2))
        #print "dimensiones"
        #print dimensiones
        v1, v2 = [f1.get(d, 0) for d in dimensiones], [f2.get(d, 0) for d in dimensiones]
        #print "vectores"
        #print [v1, v2]
        ret = self.cosine(v1, v2) * 100
        #print "coseno: " + str(ret)
        return ret

    def similarity(self, text1, text2, b=0.9):
        unigrams = self.distance(text1, text2, 1)
        bigrams = self.distance(text1, text2, 2)

        b_2 = pow(b, 2)

        # similarity = (1+b_2) * ((unigrams * bigrams) / ((b_2 * unigrams) + bigrams))
        partial = ((b_2 * unigrams) + bigrams)
        
        if bigrams == 0.0 :
            bigrams = 0.19

        if partial != 0.0:
            similarity = (1+b_2) * ((unigrams * bigrams) / partial)
        else:
            similarity = 0.0

        if numpy.isnan(similarity):
            similarity = 0.0

        return similarity

    def relevant_entities_coincidence(self, newsItem1, newsItem2):
        coincidences_count = 0
        for entity in self._top_five(newsItem1.entities):

            coincidences = [e for e in self._top_five(newsItem2.entities) if entity['name'] == e['name']]
            # and entity['semantic'] == e['semantic']]
            if len(coincidences) > 0:
                coincidences_count += 1

        return coincidences_count

    def _top_five(self, entities):
        """
        get the entities within the first 5 top scores levels
        (include multiple entities in with the same score as one level)
        """
        if len(entities) <= 0:
            return []

        current = entities[0]['score']
        count = 1

        top5entities = []

        for idx, entity in enumerate(entities[1:]):
            if entity['score'] != current:
                if count == 5:
                    top5entities = entities[:idx]
                    break
                else:
                    count += 1
                    current = entity['score']

        if count < 5:
            top5entities = entities

        return top5entities
