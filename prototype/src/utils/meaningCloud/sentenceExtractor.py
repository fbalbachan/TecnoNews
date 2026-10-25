# -*- coding: utf-8 -*
from src.utils.meaningCloud.model.sentence.sentence import Sentence


class SentenceExtractor(object):
    def __init__(self, global_map):
        self.global_map = global_map

    def extract(self):
        sentences = []
        for key, value in self.global_map.items():
            if 'type' in value and value['type'] == 'sentence':
                sentences.append(Sentence(value))
        return sentences
