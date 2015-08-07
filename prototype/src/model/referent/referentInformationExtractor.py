# -*- coding: utf-8 -*-
from collections import Counter


class ReferentInformationExtractor:
    def __init__(self, referent):
        self.referent = referent

    def extract(self):
        words = []

        for reference in self.referent.explicit_references():
            if reference.father:
                reference = reference.father
            words.extend([leaf.lexical_form for leaf in reference.node.leaves_of_category("noun")])

        return [word for word, freq in Counter(words).most_common(3)]  # @UnusedVariable

    @staticmethod
    def update_named_referents_of(paragraph):
        for referent in paragraph.named_referents():
            referent.extra_words = ReferentInformationExtractor(referent).extract()