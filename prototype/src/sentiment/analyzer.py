#!/usr/bin/python
# -*- coding: utf-8 -*-
from model.structure import *
from utils.freeling_utils import FreelingAnalyzer
from ling.msi_mapper import *
from ling.verb_categories import *
from ling.tacit_subjects import *
from ling.verb_info import *

def load_sentiwordnet():
    sentiwordnet_file = 'resources/sentiwordnet.csv'
    sentiwordnet_file_reader = unicode_csv_reader(codecs.open(sentiwordnet_file, 'r', 'utf-8'), first_line_is_header=False, delimiter=',')
    words_with_sentiment = {}
    for line in sentiwordnet_file_reader:
        word, word_class, positive_sentiment, negative_sentiment = line[0], line[1], float(line[2]), float(line[3])
        words_with_sentiment[word] = (word, word_class, positive_sentiment, negative_sentiment)
    return words_with_sentiment

class SentimentAnalyzer(object):

    def __init__(self):
        self.words_with_sentiment = load_sentiwordnet()

    def assign_sentiment_via_adverbial_criterion(self, sentence):
        evidence = u""
        sentiment = (sentence.subject.sentiment[0], sentence.subject.sentiment[1]) # start from existing sentiment

        adverbs = filter(lambda word: word.tag == 'RG', sentence.all_words)
        if adverbs:
            adverbs_with_sentiment = [self.words_with_sentiment[adverb.lemma] for adverb in adverbs if self.words_with_sentiment.has_key(adverb.lemma)]
            pos, neg = 0.0, 0.0 
            for adverb_with_sentiment in adverbs_with_sentiment: # add sentiment for each adverb
                pos += adverb_with_sentiment[2]
                neg += adverb_with_sentiment[3]
                evidence += u"\nupdating sentiment via adverbial criterion: (word: %s, %s, positive: %d, negative: %d)" % (adverb_with_sentiment[0], adverb_with_sentiment[1] == u'VERBO' and u'VERB' or u'NOT_VERB', adverb_with_sentiment[2], adverb_with_sentiment[3])

            sentiment = (sentiment[0] + pos, sentiment[1] + neg)

        return (sentiment, evidence)

    def assign_sentiment_via_nominal_criterion(self, sentence):
        evidence = u""
        sentiment = (0.0, 0.0)
        
        return (sentiment, evidence)
