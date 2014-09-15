# -*- coding: utf-8 -*-

class ReferentRanker:
    def __init__(self, paragraph):
        self.paragraph = paragraph

    def rank(self):
        functions_by_entity = self.arrange_entities_by_function()

        score_by_referent = {}

        for referent in self.paragraph.referents():
            score = 0
            for reference in referent.references:
                score += sum(self.score_by_function[function] for function in functions_by_entity[reference])
            score_by_referent[referent] = score

        ranking = sorted(score_by_referent.items(), key = lambda (referent, score): score, reverse = True)
        return ranking

    def arrange_entities_by_function(self):
        # Una entidad puede estar también en una cláusula relativa, ver https://trello.com/c/K8mU9Fg0
        functions_by_entity = {}

        for clause in self.paragraph.clauses():
            for structure in clause.syntactic_structures:
                for entity in structure.all_entities():
                    if not entity in functions_by_entity: functions_by_entity[entity] = []
                    functions_by_entity[entity].append(structure.name)
                    for children in entity.children:
                        if not children in functions_by_entity: functions_by_entity[children] = []
                        functions_by_entity[children].append(structure.name)

        return functions_by_entity

    score_by_function = {"subject" : 1, "od" : 0.75, "oi" : 0.75, "regimen" : 0.75, "equative" : 0.75,
                         "adjuncts" : 0.5, "instrument_goal" : 0.5 }