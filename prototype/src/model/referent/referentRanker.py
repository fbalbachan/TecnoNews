# -*- coding: utf-8 -*-

class ReferentRanker:
    def __init__(self, paragraph):
        self.paragraph = paragraph

    def rank(self):
        """

        :rtype : list of tuples, each tuple is (Referent, score) where score is int or float
        """
        functions_by_entity = self.arrange_entities_by_function()

        score_by_referent = {}

        for referent in self.paragraph.named_referents():
            score = 0
            for reference in referent.references:
                if reference in functions_by_entity:
                    score += sum(self.score_by_function[function] for function in functions_by_entity[reference])
            score_by_referent[referent] = score

        ranking = sorted(list(score_by_referent.items()),
                         key = lambda p_referent_p_score: (p_referent_p_score[1], - p_referent_p_score[0].first_occurrence().token.start()),
                         reverse = True)
        return ranking

    def arrange_entities_by_function(self):
        # Una entidad puede estar también en una cláusula relativa, ver https://trello.com/c/K8mU9Fg0
        functions_by_entity = {}

        for clause in self.paragraph.clauses():
            for structure in clause.syntactic_structures:
                for entity in structure.all_entities():
                    if entity not in functions_by_entity:
                        functions_by_entity[entity] = []
                    functions_by_entity[entity].append(structure.name)
                    for children in entity.children:
                        if children not in functions_by_entity:
                            functions_by_entity[children] = []
                        functions_by_entity[children].append(structure.name)

        return functions_by_entity

    score_by_function = {"subject":         1,
                         "od":              0.5,
                         "oi":              0.5,
                         "regimen":         0.5,
                         "equative":        0.5,
                         "adjuncts":        0.25,
                         "instrument_goal": 0.25 }
