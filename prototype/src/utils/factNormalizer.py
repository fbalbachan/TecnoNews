#-*- coding: utf-8 -*-

class FactNormalizer():
    def __init__(self, clause):
        self.clause = clause

    def fact(self):
        fact = ""
        clause = self.clause
        # structure_order = ["subject", "verb", "od", "oi", "regimen", "equative", "instrument_goal", "adjuncts"]
        structure_order = ["subject", "verb", "od", "regimen", "equative", "oi"]

        for structure_name in structure_order:
            if clause.has_structure(structure_name):
                if fact:
                    fact += " + "
                structure = clause.structure(structure_name)
                if structure.is_empty():
                    fact += "∅"
                else:
                    entities = [self.string_of(entity) for entity in structure.all_entities()]
                    if structure_name == "verb" and clause.is_negated():
                        fact += "no "
                    fact += ", ".join(entities)
        
        time_lexical_forms = [" ".join([repr(l) for l in reference.leaves()]) for reference in clause.time_references]
        fact = fact + " --TIME: " + ", ".join(time_lexical_forms)
        return fact

    def string_of(self, entity):
        if entity.is_linked(): entity = entity.referenced()

        if entity.category() == "verb":
            return entity.lemma()

        if entity.is_tacit() or entity.is_impersonal():
            return entity.lexical_form

        lemmas = [leaf.lemma for leaf in entity.leaves()]
        if lemmas == ["quién"]:
            return "alguien"

        if lemmas == ["qué"] \
                and entity.msi["category"] == "pronoun" \
                and entity.msi["type"] == "interrogative":
            return "algo"

        return str(entity)
