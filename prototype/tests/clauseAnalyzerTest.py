#!/usr/bin/env python
#-*- coding: utf-8 -*-
from ast import literal_eval
import unittest

from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentence import Sentence
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from tests.freelingTreeRepository import FreelingTreeRepository


class TestClauseAnalyzer(unittest.TestCase):

    def setUp(self):
        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        self.analyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def test(self):
        self.run_test_file("tests/input/context.txt")
        self.run_test_file("tests/input/global_operators.txt")
        self.run_test_file("tests/input/valuated_adverbs.txt")
        self.run_test_file("tests/input/sentiment.txt")

    def run_test_file(self, file):

        frame = {}

        test_file = open(file)
        line_number = 0
        for line in test_file:
            line_number = line_number + 1
            line = line.strip("\n").strip(" ").replace("\t", "")
            if not line or self.is_comment(line): continue

            if self.begin_with_keyword(line):
                self.update_frame_and_assert(line, frame)
            else:
                print "Analyzing [" + file + ":" + str(line_number) + "]:", line
                paragraph = Paragraph.from_text(line)
                self.analyzer.analyze(paragraph)
                frame = { "paragraph" : paragraph }

                if len(paragraph.sentences) == 1:
                    self.sentence(line, frame)

    def show_info_for(self, sentence):
        #print sentence.parse_node.tree_representation()
        print "Clauses"
        for clause in sentence.clauses:
            empty_structures = []
            print "\t", clause
            for structure in clause.syntactic_structures:
                if structure.is_empty():
                    empty_structures.append(structure.name)
                else:
                    print "\t  ", structure.name, structure
            print "\t   Empty structures", ", ".join(empty_structures)
            print
            print "\t   Global operators", list(clause.global_operators)
            print "\t   Valuated adverbs", list(clause.valuated_adverbs)
            print

            entities = clause.entities
            if entities:
                print "\t Entities"
                for entity in clause.entities:
                    print "\t  ", entity.sentimental_value

            entities = clause.tacit_entities()
            if entities:
                print "\t Tacit entities"
                for entity in entities:
                    print "\t  ", entity.sentimental_value
        print "--"

    def sentence(self, assertion, frame):
        paragraph = frame["paragraph"]
        sentences = filter(lambda sentence: str(sentence) == assertion, paragraph.sentences)
        self.assertTrue(len(sentences) == 1, "No se encontró la oración " + assertion)

        sentence = sentences[0]
        frame["sentence"] = sentence
        self.show_info_for(sentence)

        if len(sentence.clauses) == 1: self.clause(str(sentence.clauses[0]), frame)

    def update_frame_and_assert(self, assertion, frame):
        string = assertion
        splitted = string.split(":")
        keyword = splitted[0]
        assertion = ":".join(splitted[1:]).strip(" ")

        if keyword in self.structure_keywords:
            self.update_frame_and_assert_structure(keyword, assertion, frame)
        else:
            getattr(self, keyword)(assertion, frame)

    def update_frame_and_assert_structure(self, structure_name, assertion, frame):
        clause = frame["clause"]

        self.assertTrue(clause.has_structure(structure_name), "No existe " + structure_name)
        structure = clause.structure(structure_name)
        frame["structure"] = structure
        if "entity" in frame: del frame["entity"]

        if len(structure.all_entities()) == 1:
            frame["entity"] = structure.all_entities()[0]
            self.entity(assertion, frame)
        else:
            self.assertEqual("", assertion, "Existe más de una entidad (o ninguna) para " + structure_name)

    def count(self, assertion, frame):
        splitted = assertion.split("=")
        assertions = { "entities" : lambda: len(frame["structure"].all_entities()),
                       "go": lambda: len(frame["clause"].global_operators),
                       "adverbs": lambda: len(frame["clause"].valuated_adverbs),
                       "sent_ev": lambda: len(frame["entity"].sentimental_value.evidence())
                       }
        if len(splitted) == 1: splitted = [ "entities", splitted[0] ]

        assertion = splitted[0].strip()
        expected = int(splitted[1].strip())

        self.assertEqual(assertions[assertion](), expected, "Count for '" + assertion + "' is not " + str(expected))

    def entity(self, assertion, frame):
        entities = frame["structure"].all_entities()
        asserted_lexical_forms = assertion.split(" -> ")
        if len(asserted_lexical_forms) > 1:
            entities = self.search_linked_entity(asserted_lexical_forms, entities)
        else:
            entities = self.search_non_linked_entity(assertion, entities)

        self.assertTrue(len(entities) == 1, "No se encontró la entidad " + assertion + " en " + frame["structure"].name)

        entity = entities[0]
        frame["entity"] = entity

    def search_non_linked_entity(self, lexical_form, entities):
        return filter(lambda entity: not entity.is_linked() and entity.lexical_form == lexical_form, entities)

    def search_linked_entity(self, lexical_forms, entities):
        return filter(lambda entity: entity.is_linked() and entity.lexical_form == lexical_forms[0]
                          and entity.referenced().lexical_form == lexical_forms[1], entities)

    def sent_ev(self, assertion, frame):
        entity = frame["entity"]
        evidence = entity.sentimental_value.evidence()
        found = filter(lambda each: each.object.lexical_form == assertion, evidence)
        self.assertTrue(len(found) == 1, "No se encontró (o hay más de una) evidencia con forma léxica " + assertion)
        frame["sent_ev"] = found[0]

    def value(self, assertion, frame):
        evaluation = frame["sent_ev"]
        self.assertEqual(evaluation.value, literal_eval(assertion))

    def lemma(self, assertion, frame):
        entity = frame["entity"]
        self.assertEqual(assertion, entity.lemma())

    def msi(self, assertion, frame):
        entity = frame["entity"]
        msi = entity.msi
        expected_msi = literal_eval(assertion)

        for attribute, value in expected_msi.items():
            self.assertTrue(attribute in msi)
            actual_value = msi[attribute]
            message = "Attribute " + str(attribute) + ": '" + str(value) + "' != '" + str(actual_value) + \
                "' \nFrame " + str(frame)
            self.assertEqual(value, actual_value, message)

    def clause(self, assertion, frame):
        sentence = frame["sentence"]
        clauses = filter(lambda clause: str(clause) == assertion, sentence.clauses)
        self.assertTrue(len(clauses) == 1, "No se encontró la cláusula " + assertion)
        frame["clause"] = clauses[0]

    def adverb(self, assertion, frame):
        clause = frame["clause"]
        adverb_lexical_forms = [ adverb.lexical_form for adverb in clause.valuated_adverbs ]
        self.assertTrue(assertion in adverb_lexical_forms,
                        "La cláusula no tiene un adverbio valuado sentimentalmente de forma léxica " + assertion)

    def go(self, assertion, frame):
        clause = frame["clause"]
        self.assertTrue(clause.has_global_operator_of(assertion),
                        "La cláusula no tiene un operador global de tipo " + assertion)

    def begin_with_keyword(self, string):
        string = string.replace(" ", "")
        return any(( string.startswith(keyword + ":") for keyword in self.keywords ))

    def is_comment(self, string):
        return string.startswith("#")

    structure_keywords = [ "subject", "od", "oi", "equative", "regimen", "instrument_goal", "adjuncts", "verb" ]
    keywords = [ "clause", "lemma", "msi", "entity", "sentence", "count", "go", "adverb", "sent_ev", "value" ] + \
        structure_keywords

if __name__ == '__main__':
    unittest.main()
