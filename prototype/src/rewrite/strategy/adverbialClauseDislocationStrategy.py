# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case
from src.parser.leafNode import LeafNode
from src.parser.labelNode import LabelNode
from src.model.go.conditionFinder import ConditionFinder
from src.rewrite.strategy.siAEncasodequeStrategySubjunctivePart import SiAEncasodequeStrategySubjunctivePart

import src.rewrite.rewriter
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from tests.freelingTreeRepository import FreelingTreeRepository


class AdverbialClauseDislocationStrategy:
    def __init__(self, ontology, changeHeaderIfPossible = True):
        self.ontology = ontology
        self.changeHeaderIfPossible = changeHeaderIfPossible

    def applies_to(self, sentence, node):
        en_caso_de_que = (
            isinstance(node, LabelNode) and node.label == 'prep' and
            self.encasode_subord_node(node)
            # TODO: Terminar este código!!!
            #self.is_subord_to_apply(node.children[0], ["que"]) and
            #len(ConditionFinder(main_clause.children[0].children[0]).find()) > 0 and
            #ConditionFinder(main_clause.children[0].children[0]).find()[0].object == 'en_caso_de'
        )
        return self.is_subord_to_apply(node) or en_caso_de_que

    def is_subord_to_apply(self, node, subordinate_headers = None):
        return isinstance(node, LabelNode) and node.label == 'grup-verb' and self.subord_node(node, subordinate_headers)
        # TODO: Revisar este comentario
        """
        return (
            node.label == 'grup-verb' and self.exists(node, subordinate_headers)
            len(node.children) > 0 and
            clause.children[0].node.label == 'subord' and (
                clause.children[0].node.token.start() == clause.node.token.start() or
                len(ConditionFinder(clause.children[0]).find()) == 0
            ) and
            clause.children[0].node.leaves()[0].lemma in subordinate_headers
        )
        return (
            clause.node.label == 'grup-verb' and len(clause.children) > 0 and
            clause.children[0].node.label == 'subord' and (
                clause.children[0].node.token.start() == clause.node.token.start() or
                len(ConditionFinder(clause.children[0]).find()) == 0
            ) and
            clause.children[0].node.leaves()[0].lemma in subordinate_headers
        )
        """

    def subord_node(self, node, subordinate_headers = None):
        if subordinate_headers == None: subordinate_headers = self.subordinate_headers
        for i in xrange(len(node.children)):
            child = node.children[i]
            if isinstance(child, LabelNode) and child.label == 'subord':
                if len(child.children) > 0:
                    grandson = child.children[0]
                    if isinstance(grandson, LeafNode) and grandson.lemma in subordinate_headers:
                        return child
        return None

    # TODO: Terminar en caso de que!!
    def encasode_subord_node(self, node):
        for i in xrange(len(node.children)):
            child = node.children[i]
            if isinstance(child, LeafNode) and child.lemma == 'en_caso_de' and i + 1 < len(node.children):
                possible_subord = node.children[i+1]
                if isinstance(possible_subord, LabelNode) and possible_subord.label == 'subord' and len(possible_subord.children) > 0:
                    possible_que = possible_subord.children[0]
                    if isinstance(possible_que, LeafNode) and possible_que.lemma == 'que':
                        return possible_subord
        return None

    def rewrite(self, sentence, node):
        if self.is_subord_to_apply(node):
            subord_node = self.subord_node(node)
            if node.token.start() == subord_node.token.start():
                return self.rewrite_if_p_q(sentence, node, subord_node)
            else:
                return self.rewrite_q_if_p(sentence, node, subord_node)
        else:
            subord_node = self.encasode_subord_node(node)
            return self.rewrite_en_caso_de_que_p_q(sentence, node, subord_node)

    # TODO: Move this method to Clause
    def clause_is_or_inherits_from(self, clause, label):
        node = clause.node
        while node:
            if node.label == label: return True
            node = node.father
        return False

    def rewrite_if_p_q(self, sentence, node, subord_node):
        text = sentence.paragraph.text.decode("utf-8")
        first_part = text[node.token.start():subord_node.token.end()].strip()
        second_part = text[subord_node.token.end():node.token.end()].strip()

        final_punctuation = "" # TODO: Tomar toda la puntuación del final de second_part
        if len(second_part) > 0 and second_part[-1] == ".": # TODO: Hacerlo bien: Si soy esto, soy esto!. (múltiples puntuaciones)
            final_punctuation = "."
            second_part = second_part[:-1]

        if first_part[-1] == ",":
            first_part = first_part[:-1]

        second_part += ","
        second_part = set_first_letter_case(first_part, second_part)

        # first_part[0] nunca debe ser mayúscula ya que comienza con condicionales
        first_part = first_part[0].lower() + first_part[1:]

        if self.changeHeaderIfPossible:
            if subord_node.leaves()[0].lemma == 'si':
                first_part = self.rewrite_si_a_encasode(first_part)
            elif first_part[:7] == "apenas ":
                first_part = "cuando " + first_part[7:]

        rewritten_sentence = second_part + " " + first_part + final_punctuation
        return Rewrite(node, rewritten_sentence.encode('utf-8'))

    # Si p => En caso de que subjuntivo(p)
    def rewrite_si_a_encasode(self, first_part):
        siAEncasodeque = [ SiAEncasodequeStrategySubjunctivePart(self.ontology) ]
        paragraph = Paragraph.from_text(first_part.encode('utf-8'))
        self.analyzer.analyze(paragraph)

        not_subord_rel = [ c for c in paragraph.clauses() if not self.clause_is_or_inherits_from(c, 'subord-rel') ]
        subjunctive_first_part = src.rewrite.rewriter.Rewriter(
            paragraph, self.ontology, siAEncasodeque, not_subord_rel
        ).rewrite().decode('utf-8')

        if first_part != subjunctive_first_part and subjunctive_first_part[:3].lower() == 'si ':
            return set_first_letter_case(subjunctive_first_part, "en caso de que ") + subjunctive_first_part[3:]
        return first_part

    def rewrite_q_if_p(self, sentence, node, subord_node):
        text = sentence.paragraph.text.decode("utf-8")
        first_part = text[node.token.start():subord_node.token.start()].strip()
        second_part = text[subord_node.token.start():subord_node.token.end()].strip()
        third_part = text[subord_node.token.end():node.token.end()].strip()

        final_punctuation = "" # TODO: Tomar toda la puntuación del final de third_part
        if len(third_part) > 0 and third_part[-1] == ".": # TODO: Hacerlo bien: Si soy esto, soy esto!. (múltiples puntuaciones)
            final_punctuation = "."
            third_part = third_part[:-1]

        if first_part[-1] == ",":
            first_part = first_part[:-1]

        if second_part[-1] != ",":
            second_part += ","
        second_part = set_first_letter_case(first_part, second_part)

        if self.changeHeaderIfPossible:
            if subord_node.leaves()[0].lemma == 'si':
                second_part = self.rewrite_si_a_encasode(second_part)
            elif second_part[:7].lower() == "apenas ":
                second_part = set_first_letter_case(first_part, "cuando ") + second_part[7:]

        # TODO: Evaluar los casos donde esto no debe hacerse! (Ej: nombres propios)
        first_part = first_part[0].lower() + first_part[1:]
        if len(third_part) > 0:
            # TODO: Evaluar los casos donde esto no debe hacerse! (Ej: nombres propios)
            third_part = " " + third_part[0].lower() + third_part[1:]

        rewritten_sentence = second_part + " " + first_part + third_part + final_punctuation
        return Rewrite(node, rewritten_sentence.encode('utf-8'))

    def rewrite_en_caso_de_que_p_q(self, sentence, node, subord_node):
        main_clause = sentence.main_clause()
        clause = main_clause.children[0]
        token = clause.children[0].node.token
        
        text = sentence.paragraph.text.decode("utf-8")
        first_part = text[clause.node.token.start():token.end()].strip()
        second_part = text[token.end():clause.node.token.end()].strip()

        final_punctuation = "" # TODO: Tomar toda la puntuación del final de second_part
        if len(second_part) > 0 and second_part[-1] == ".": # TODO: Hacerlo bien: Si soy esto, soy esto!. (múltiples puntuaciones)
            final_punctuation = "."
            second_part = second_part[:-1]

        if first_part[-1] == ",":
            first_part = first_part[:-1]

        second_part += ","
        second_part = set_first_letter_case(text[main_clause.node.token.start()], second_part)

        # first_part[0] nunca debe ser mayúscula ya que comienza con "en caso de"
        first_part = first_part[0].lower() + first_part[1:]

        rewritten_sentence = second_part + " en caso de " + first_part + final_punctuation
        return Rewrite(main_clause.node, rewritten_sentence.encode('utf-8'))

    type = "dislocation"

    # "en_caso_de" se ve por separado en applies_to()
    subordinate_headers = ["si", "mientras", "cuando", "una_vez_que", "según", "mientras_que"]
    sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
    analyzer = ParagraphAnalyzer(sentenceAnalyzer)
