#-*- coding: utf-8 -*-
from src.model.go.globalOperator import GlobalOperator

class TotalQuestionAnalyzer:
    def __init__(self, sentence):
        self.sentence = sentence

    def analyze(self):
        if not self.is_question() or self.has_invalid_pronouns(): return

        operator = GlobalOperator("question")
        for clause in self.sentence.clauses_of_level(0): clause.global_operators.add(operator)

    def has_invalid_pronouns(self):
        leaves = self.sentence.parse_node.leaves()
        return bool(filter(lambda leaf: (leaf.msi["category"] == "pronoun" and leaf.msi["type"] == "interrogative")
                           or (leaf.msi["category"] == "determinant" and leaf.msi["type"]
                               in ["interrogative", "exclamative"]), leaves))

    def is_question(self):
        lexical_forms = [ leaf.lexical_form for leaf in self.sentence.parse_node.leaves() ]

        last_two = [ form for form in lexical_forms[-2:] ]
        last = last_two[-1:]

        if not (last == ["?"] and last_two != ["!", "?"]): return False

        if "," in lexical_forms:
            index_of_comma = lexical_forms.index(",")
            middle_words = lexical_forms[index_of_comma + 1:-1]
            if len(middle_words) == 1: return False
        return True