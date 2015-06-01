# -*- coding: utf-8 -*-


class SyntacticStructureEntityValidator:
    def __init__(self, structure):
        self.structure = structure
        self.clause = structure.clause

    def accept(self, entity):
        name = self.structure.name
        # print "--> SyntacticStructureEntityValidator.accept(entity) - entity: ", entity, " - structure: ", name
        rule_by_structure_name = {"subject": SyntacticStructureEntityValidator.subject_accept,
                                  "od": SyntacticStructureEntityValidator.od_accept}
        if name not in rule_by_structure_name:
            return True
        accepting_rule = rule_by_structure_name[name]
        result = accepting_rule(entity, self.clause)
        return result

    @staticmethod
    def subject_accept(entity, clause):
        # print "--> SyntacticStructureEntityValidator.subject_accept(entity) - entity: ", entity
        if clause.voice == "active":
            result = entity.is_impersonal() or clause.verb.matches(entity)
        else:
            result = True

        return result

    @staticmethod
    def od_accept(entity, clause):
        result = clause.verb.matches(entity) if clause.voice == "passive" else True
        return result