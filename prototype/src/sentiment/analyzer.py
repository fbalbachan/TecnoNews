#!/usr/bin/python
# -*- coding: utf-8 -*-
from structure import *
from utils.freeling_utils import FreelingAnalyzer
from ling.msi_mapper import *
from ling.verb_categories import *
from ling.tacit_subjects import *
from ling.verb_info import *

def get_sentiwordnet():
    sentiwordnet_file = 'resources/sentiwordnet.csv'
    sentiwordnet_file_reader = unicode_csv_reader(codecs.open(sentiwordnet_file, 'r', 'utf-8'), first_line_is_header=False, delimiter=',')
    words_with_sentiment = {}
    for line in sentiwordnet_file_reader:
        word, word_class, positive_sentiment, negative_sentiment = line[0], line[1], float(line[2]), float(line[3])
        words_with_sentiment[word] = (word, word_class, positive_sentiment, negative_sentiment)
    return words_with_sentiment

class Sentence(object):

    self.words_with_sentiment = get_sentiwordnet()

    def __init__(self):
        pass

    def assign_sentiment_via_adverb(self):
        adverbs = [leaf.words[0] for leaf in self.sentence.leaves if leaf.words[0].tag == 'RG']
        if adverbs:
            adverbs_with_sentiment = [self.words_with_sentiment[adverb.lemma] for adverb in adverbs
                                      if self.words_with_sentiment.has_key(adverb.lemma)]
            for adverb_with_sentiment in adverbs_with_sentiment:
               self.subject.sentiment = (self.subject.sentiment[0] + adverb_with_sentiment[2],
                                         self.subject.sentiment[1] + adverb_with_sentiment[3])
