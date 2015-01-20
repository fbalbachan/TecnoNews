#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

import nltk
import re

import numpy


class TextDistance(object):

    def __init__(self):
        self.valid_token_regex = re.compile(r'[áéíóúñäëïöüáàâéèêíìîóòôúùûãçêôõø]*(\w+)[áéíóúñäëïöüáàâéèêíìîóòôúùûãçêôõø]*(\w*)')
        self.tokenizer_custom = nltk.tokenize.RegexpTokenizer(self.valid_token_regex)

    @staticmethod
    def cosine(x, y):
        return nltk.cluster.cosine_distance(numpy.array(x),
                                        numpy.array(y))

    def title_distance(self, title1, title2):
        from nltk import jaccard_distance
        word_set1 = set(self.tokenize(title1))
        word_set2 = set(self.tokenize(title2))
        return jaccard_distance(word_set1, word_set2)

    def tokenize(self, text):
        return self.tokenizer_custom.tokenize(text.strip().lower())

    def distance(self, text1, text2, n):
        tokens1, tokens2 = self.tokenize(text1), self.tokenize(text2)
        ngrams1, ngrams2 = nltk.ngrams(tokens1, n), nltk.ngrams(tokens2, n)
        f1, f2 = nltk.FreqDist(ngrams1), nltk.FreqDist(ngrams2)
        dimensiones = set(ngrams1).union(set(ngrams2))
        v1, v2 = [f1.get(d, 0) for d in dimensiones], [f2.get(d, 0) for d in dimensiones]
        return self.cosine(v1,v2) * 100

    def similarity(self, text1, text2, B=0.9):
        unigrams = self.distance(text1, text2, 1)
        bigrams = self.distance(text1, text2, 2)
        B_2 = pow(B, 2)

        try:
            similarity = (1+B_2) * ((unigrams * bigrams) / ((B_2 * unigrams) + bigrams))
        except ZeroDivisionError:
            similarity = 0.00

        if numpy.isnan(similarity):
            return 0
        else:
            return similarity


    def relevant_entities_coincidence(self, newsItem1, newsItem2):
        from pprint import pprint
        # import logging
        # logger = logging.getLogger()
        # logger.info("\ncomparing: ")
        # logger.info("\t%s Entities:" % newsItem1.url)
        # logger.info("\t%s", self._top_five(newsItem1.entities))
        # logger.info("With:")
        # logger.info("\t%s Entities:" % newsItem2.url)
        # logger.info("\t%s", self._top_five(newsItem2.entities))

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
        (include miltiple entities in with the same score as one level)
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
