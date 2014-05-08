# -*- coding: utf-8 -*-

class WebOutputUtils:

    def structure(self, clause, name):
        if clause.has_structure(name):
            structure = clause.structure(name)
            if name == "verb":
                return structure.entity().lemma()
            else:
                return ", ".join([ str(entity) for entity in structure.all_entities() ])
        else:
            return ""

    def tooltip(self, clause, name):
        if clause.has_structure(name):
            return ", ".join([ self.entity_tooltip(entity) for entity in clause.structure(name).all_entities() ])
        else:
            return ""

    def entity_tooltip(self, entity):
        tooltip = self.msi_string(entity.msi)
        if entity.category() == "verb":
            tooltip = tooltip + " - Transitivity " + entity.transitivity + " - Sentiment script " + entity.script_class
        return tooltip

    def msi_string(self, msi):
        return str(msi["person"]) + "° " + str(msi["gender"]) + " " + str(msi["number"]) + " (" + str(msi["category"]) + ")"
        #return ", ".join([ key + " = " + str(value) for (key, value) in msi.items() ])

    def clause_number(self, clause, sentence):
        number_string = ""
        while not clause.is_root():
            father = clause.father
            number = father.children.index(clause) + 1
            number_string = "." + str(number) + number_string
            clause = father

        number = sentence.clauses.index(clause) + 1
        number_string = str(number) + number_string

        return number_string