#-*- coding: utf-8 -*-

class FactNormalizer():
    def __init__(self, clause):
        self.clause = clause

    def fact(self):
        fact = ""
        clause = self.clause
        structure_order = [ "subject", "verb", "od", "oi", "regimen", "equative", "instrument_goal", "adjuncts" ]

        for structure_name in structure_order:
            if clause.has_structure(structure_name):
                if fact: fact = fact + " + "
                structure = clause.structure(structure_name)
                if structure.is_empty():
                    fact = fact + "∅"
                else:
                    entities = [ self.string_of(entity) for entity in structure.all_entities() ]
                    fact = fact + ", ".join(entities)
        return fact

    def string_of(self, entity):
        if entity.category() == "verb": return entity.lemma()
        if not entity.is_tacit():
            lemmas = [ leaf.lemma for leaf in entity.leaves() ]
            if lemmas == [ "quién"]: return "alguien"
            if lemmas == [ "qué" ] and entity.msi["category"] == "pronoun" and entity.msi["type"] == "interrogative":
                return "algo"

        if entity.is_linked() or entity.is_tacit(): return entity.lexical_form
        return str(entity)