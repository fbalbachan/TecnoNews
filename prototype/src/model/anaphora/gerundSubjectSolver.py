#-*- coding: utf-8 -*-
from src.ling.tacit_subjects import somebody

class GerundSubjectSolver:
    def __init__(self, clause):
        self.clause = clause

    def solve(self):
        clause = self.clause
        subject = clause.structure("subject")

        if clause.is_root():
            subject.tacit_entities = [ somebody() ]
            return

        father = clause.father
        if father.has_structure("subject") and not father.structure("subject").is_empty():
            father_subject = father.structure("subject")
            entity = father_subject.entity()
            if father_subject.is_tacit():
                subject.tacit_entities = [ entity ]
            else:
                subject.entities = [ entity ]