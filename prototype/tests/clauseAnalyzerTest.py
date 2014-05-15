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

    def test(self):
        sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        analyzer = ParagraphAnalyzer(sentenceAnalyzer)

        frame = {}

        test_file = open("tests/input/context.txt")
        for line in test_file:
            line = line.strip("\n").strip(" ").replace("\t", "")
            if not line or self.is_comment(line): continue

            if self.begin_with_keyword(line):
                self.update_frame_and_assert(line, frame)
            else:
                print "Analyzing:", line
                paragraph = Paragraph.from_text(line)
                analyzer.analyze(paragraph)
                frame = { "paragraph" : paragraph }

                if len(paragraph.sentences) == 1:
                    self.sentence(line, frame)

    def show_info_for(self, sentence):
        print sentence.parse_node.tree_representation()
        print "Clauses"
        for clause in sentence.clauses:
            print "\t", clause
            for structure in clause.syntactic_structures:
                print "\t  ", structure.name, structure
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
            self.assertEqual("", assertion, "Existe más de una entidad para " + structure_name)

    def count(self, assertion, frame):
        entities = frame["structure"].all_entities()
        self.assertEqual(len(entities), int(assertion))

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
        return filter(lambda entity: entity.is_linked() and entity.lexical_form == lexical_forms[1]
                          and entity.source.lexical_form == lexical_forms[0], entities)

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
    keywords = [ "clause", "lemma", "msi", "entity", "sentence", "count" ] + structure_keywords

if __name__ == '__main__':
    unittest.main()
