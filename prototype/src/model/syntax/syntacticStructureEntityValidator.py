# -*- coding: utf-8 -*-

class SyntacticStructureEntityValidator:
    def __init__(self, structure):
        self.structure = structure
        self.clause = structure.clause

    def accept(self, entity):
        rule_by_structure_name = {"subject": SyntacticStructureEntityValidator.subject_accept,
                                  "od": SyntacticStructureEntityValidator.od_accept}
        name = self.structure.name
        if name not in rule_by_structure_name:
            return True
        rule = rule_by_structure_name[name]
        return rule(entity, self.clause)

    @staticmethod
    def subject_accept(entity, clause):
        if clause.voice == "active":
            result = entity.is_impersonal() or clause.verb.matches(entity)
        else:
            result = True

        return result

    @staticmethod
    def od_accept(entity, clause):
        result = clause.verb.matches(entity) if clause.voice == "passive" else True
        return result