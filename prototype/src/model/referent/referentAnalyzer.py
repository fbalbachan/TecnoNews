# -*- coding: utf-8 -*-
from src.model.entity.entityMatchingAnalyzer import EntityMatchingAnalyzer

class ReferentAnalyzer:
    def __init__(self, paragraph):
        self.paragraph = paragraph

    def unify(self):
        entities = list(self.paragraph.entities())
        while len(entities) > 1:
            source = entities.pop()
            matching_analyzer = EntityMatchingAnalyzer(source)

            for other in entities:
                if matching_analyzer.matches(other): other.update_referent(source.referent)

    def analyze(self):
        self.unify()
        #self.analyze_scores()

    def analyze_scores(self):
        referent_scores = {}

        for referent in self.paragraph.referents():
            score = (0, 0)
            for entity in referent.references:
                value = entity.sentimental_value.value
                score = (score[0] + value[0], score[1] + value[1])
            n = float(referent.ref_count())
            score = (score[0] / n, score[1] / n)
            referent_scores[referent] = score

        print "scores", referent_scores
        for r in filter(lambda ref: ref.semantic_classification() == "person", referent_scores.keys()):
            print r, referent_scores[r]