#!/usr/bin/env python
#-*- coding: utf-8 -*-
from ast import literal_eval
import unittest

from src.model.sentenceAnalyzer import SentenceAnalyzer
from src.model.sentence import Sentence
from tests.freelingTreeRepository import FreelingTreeRepository


class TestClauseAnalyzer(unittest.TestCase):

    def test(self):
        analyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        frame = {}

        test_file = open("tests/input/clause_analyzer.txt")
        for line in test_file:
            line = line.strip("\n").strip(" ").replace("\t", "")
            if not line or self.is_comment(line): continue

            if self.begin_with_keyword(line):
                self.update_frame_and_assert(line, frame)
            else:
                print "Analyzing:", line
                sentence = Sentence(line)
                analyzer.analyze(sentence)
                frame = { "sentence" : sentence }

                if len(sentence.clauses) == 1:
                    frame["clause"] = sentence.clauses[0]

                self.show_info_for(sentence)

    def show_info_for(self, sentence):
        print sentence.parse_node.tree_representation()
        print "Clauses"
        for clause in sentence.clauses:
            print "\t", clause
            for structure in clause.syntactic_structures:
                print "\t  ", structure.name, structure
        print "--"

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
            self.assertEqual("", assertion, "Existe más de una entidad para " + structure_name)

    def entity(self, assertion, frame):
        entities = filter(lambda entity: entity.lexical_form == assertion, frame["structure"].all_entities())
        self.assertTrue(len(entities) == 1, "No se encontró la entidad " + assertion + " en " + frame["structure"].name)

        entity = entities[0]
        frame["entity"] = entity

        lexical_form = entity.lexical_form
        message = "Error '" + assertion + "' != '" + lexical_form + "'"
        self.assertEqual(assertion, lexical_form, message)

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

    def begin_with_keyword(self, string):
        string = string.replace(" ", "")
        return any(( string.startswith(keyword + ":") for keyword in self.keywords ))

    def is_comment(self, string):
        return string.startswith("#")

    structure_keywords = [ "subject", "od", "oi", "equative", "regimen", "adjuncts", "verb" ]
    keywords = [ "clause", "lemma", "msi", "entity" ] + structure_keywords

if __name__ == '__main__':
    unittest.main()
