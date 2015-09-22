# -*- coding: utf-8 -*-
from math import log


class SentimentalSummarizer:
    def __init__(self, paragraph):
        self.paragraph = paragraph

    def analyze(self):
        paragraph = self.paragraph
        analysis = {}
        for clause in self.paragraph.clauses():
            analysis[clause] = self.analyze_clause(clause)

        for sentence in paragraph.sentences:
            analysis[sentence] = self.summarize_clauses(sentence.clauses, analysis)

        analysis[paragraph] = self.summarize_paragraph(paragraph, analysis)

        return analysis

    def summarize_paragraph(self, paragraph, analysis):
        self.summarize_clauses(paragraph.clauses(), analysis)
        new_summary = self.normalize(analysis, paragraph)
        return new_summary

    def normalize(self, analysis, paragraph):
        normalized_summary = analysis[paragraph]
        for dimension in ["positive", "negative"]:
            if dimension not in normalized_summary:
                normalized_summary[dimension] = 0

            value = normalized_summary[dimension]
            if value >= 80:
                value = 80 + ((value - 80) / 20)
                normalized_summary[dimension] = value

        return normalized_summary

    def summarize_clauses(self, clauses, analysis):
        summary = {}
        for clause in clauses:
            clause_summary = analysis[clause]
            for dimension, value in clause_summary.items():
                if not dimension in summary: summary[dimension] = 0
                summary[dimension] = summary[dimension] + value

        n = float(len(clauses))
        for dimension, value in summary.items():
            summary[dimension] = summary[dimension] / n

        return summary

    def analyze_clause(self, clause):

        evidences = sum([entity.sentimental_value.leaves() for entity in clause.all_entities()],
                        [])

        positive_dim = lambda ev: ev.joined_value() > 0
        negative_dim = lambda ev: not positive_dim(ev)
        dimensions = [("positive", positive_dim),
                      ("negative", negative_dim)]

        summary = {}
        for dimension, belongs in dimensions:
            evidences_set = set()
            _sum = 0
            for evidence in evidences:
                if not evidence.is_neutral() and belongs(evidence):
                    evidences_set.add(evidence)
                    _sum = _sum + abs(evidence.joined_value())

            n = len(evidences_set)
            value = 0

            if n > 0:
                value = _sum * (1 / log(1 + n))

            summary[dimension] = value

        return summary
