# -*- coding: utf-8 -*-
from src.ling.tacit_subjects import somebody

debug_mode = False


class GerundSubjectSolver:
    def __init__(self, clause):
        self.clause = clause

    def solve(self):
        if debug_mode: print("--> GerundSubjectSolver.solve()")
        clause = self.clause
        subject = clause.structure("subject")

        if clause.is_root():
            subject.tacit_entities = [somebody()]
            return

        father = clause.father
        if father.has_structure("subject") and not father.structure("subject").is_empty():
            father_subject = father.structure("subject")
            entity = father_subject.entity()
            if father_subject.is_tacit():
                subject.tacit_entities = [entity]
            elif not entity.is_trace():
                subject.entities = [entity]