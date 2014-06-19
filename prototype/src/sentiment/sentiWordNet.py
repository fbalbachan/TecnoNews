# -*- coding: utf-8 -*-
import ConfigParser

from src.sentiment.wordSentimentalValue import WordSentimentalValue
from src.utils.csvwrapper import unicode_csv_reader


def load_sentiwordnet():
    Config = ConfigParser.ConfigParser()
    Config.read("config")

    sentiwordnet_file =  Config.get("resources", "sentiwordnet")
    reader = unicode_csv_reader(open(sentiwordnet_file, 'r'), first_line_is_header=False, delimiter=',')
    values_by_lemma = {}

    for lemma, verb_mark, positive, negative in reader:
        value = int(positive) - int(negative)
        word_value = WordSentimentalValue(lemma, value)
        values_by_lemma[lemma] = word_value
    return values_by_lemma

class SentiWordNet:
    @staticmethod
    def get(lemma):
        repository = SentiWordNet.values_by_lemma
        if lemma in repository: return repository[lemma]
        return WordSentimentalValue.default_for(lemma)

    values_by_lemma = load_sentiwordnet()