#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

import nltk
import re

import numpy


class TextDistance(object):

    def __init__(self):
        self.threshold = 90.00
        self.valid_token_regex = re.compile(r"""[+-<>=]?\d+([/.,:]\d+)?[°%]?(x\d+)?|\w+([-/_\\]?\w+)?""", re.U)
        self.tokenizer_custom = nltk.tokenize.RegexpTokenizer(self.valid_token_regex)

    @staticmethod
    def cosine(x, y):
        return nltk.cluster.cosine_distance(numpy.array(x),
                                        numpy.array(y))

    @staticmethod
    def title_distance(title1, title2):
        from nltk import jaccard_distance
        word_set1 = set(title1.split())
        word_set2 = set(title2.split())
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
            similarity = "0.00"

        if numpy.isnan(similarity):
            return "0.00"
        else:
            return "%.2f" % similarity


    # Most relevant list of Entities
    # @staticmethod
    # def rank_of_entities(text):
    #     from src.model.referent.referentRanker import ReferentRanker
    #     from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
    #     from src.model.paragraph.paragraph import Paragraph
    #     from src.model.referent.entityUnifier import EntityUnifier
    #
    #     analyzer = ParagraphAnalyzer()
    #     paragraph = Paragraph.from_text(text)
    #     analyzer.analyze(paragraph)
    #     EntityUnifier(paragraph).unify()
    #     return ReferentRanker(paragraph).rank()
    #
    # @staticmethod
    # def most_relevant_entities(renked_entities_list):
    #
    #     return [x[0] for i, x in enumerate(renked_entities_list) if i < 5]

    @staticmethod
    def relevant_entities_coincidence(newsItem1, newsItem2):
        # ranked_entities1 = TextDistance.rank_of_entities(text1)
        # entities_text1 = TextDistance.most_relevant_entities(ranked_entities1)
        entities_text1 = newsItem1.entities

        # ranked_entities2 = TextDistance.rank_of_entities(text2)
        # entities_text2 = TextDistance.most_relevant_entities(ranked_entities2)
        entities_text2 = newsItem2.entities

        coincidences_count = 0
        for entity in entities_text1:

            coincidences = [e for e in entities_text2 if e.name() == entity.name()
            and e.semantic_classification() == entity.semantic_classification()]
            if len(coincidences) > 0:
                coincidences_count += 1

        return coincidences_count
