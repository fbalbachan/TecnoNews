#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import unittest
from collections import Counter

from src.ling.msi_mapper import tag_to_full_msi
from src.parser.freelingTreeParser import FreelingTreeParser
from src.utils.languageDetectorClient import LanguageDetectorClient
from src.utils.spacyClientParser import SpacyClientParser

TREES_DIR = "tests/input/trees"
LEAF = re.compile(r"^\+?\(([^ ]+) ([^ ]+) (\w+) -\)$")
LABEL = re.compile(r"^\+?([-a-zA-Z]+)_\[$")


def text_of(lines):
    """Sentence of a FreeLing tree: its leaves, with the contractions FreeLing splits put back."""
    forms = [LEAF.match(line.strip()).group(1).replace("_", " ") for line in lines if LEAF.match(line.strip())]
    text = re.sub(r" ([,.;:?!])", r"\1", " ".join(forms))
    text = re.sub(r"\b([Dd])e el\b", r"\1el", text)
    return re.sub(r"\b([Aa]) el\b", r"\1l", text)


def brackets(lines):
    """Counter of (label, first leaf, last leaf) for every label node."""
    result, stack, leaves = Counter(), [], 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == "]":
            label, start = stack.pop()
            result[(label, start, leaves)] += 1
        elif LEAF.match(line):
            leaves += 1
        else:
            stack.append((LABEL.match(line).group(1), leaves))
    return result


def labels(lines):
    return [LABEL.match(line.strip()).group(1) for line in lines if LABEL.match(line.strip())]


class SpacyTreeTest(unittest.TestCase):
    """The spaCy analysis must keep producing the FreeLing trees the linguistic model was written for.
    tests/input/trees holds real FreeLing outputs (file name = sha1 of the sentence)."""

    @classmethod
    def setUpClass(cls):
        cls.parser = SpacyClientParser()
        cls.freeling = []
        for name in sorted(os.listdir(TREES_DIR)):
            lines = open(os.path.join(TREES_DIR, name), encoding="utf-8").read().split("\n")
            cls.freeling.append((text_of(lines), lines))

    def test_health_check(self):
        self.assertTrue(self.parser.health_check())

    def test_output_is_a_valid_freeling_tree(self):
        for text, _ in self.freeling:
            lines = self.parser.parse(text)
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped == "]":
                    continue
                leaf = LEAF.match(stripped)
                self.assertTrue(leaf or LABEL.match(stripped), "malformed line %r for %r" % (line, text))
                if leaf:
                    tag_to_full_msi(leaf.group(3))
            tree = FreelingTreeParser().parse(lines)
            self.assertEqual(len([line for line in lines if LEAF.match(line.strip())]), len(tree.leaves()))

    def test_agreement_with_freeling(self):
        hits = total_freeling = total_spacy = 0
        for text, freeling_lines in self.freeling:
            spacy_lines = self.parser.parse(text)
            expected, found = brackets(freeling_lines), brackets(spacy_lines)
            hits += sum(min(count, found[key]) for key, count in list(expected.items()))
            total_freeling += sum(expected.values())
            total_spacy += sum(found.values())
        recall, precision = float(hits) / total_freeling, float(hits) / total_spacy
        # measured when migrating from FreeLing: 0.91 - 0.92 with es_core_news_md 2.3 / 3.x
        self.assertGreaterEqual(recall, 0.85)
        self.assertGreaterEqual(precision, 0.85)

    def test_passive_voice(self):
        lines = self.parser.parse("La ley fue aprobada por el Senado.")
        self.assertEqual("verb-pass_[", lines[0])
        self.assertTrue({"vser", "parti-flex", "grup-sp"} <= set(labels(lines)))

    def test_subordinate_and_relative_clauses(self):
        lines = self.parser.parse("Dijo que la amaba.")
        self.assertTrue("subord" in labels(lines))
        self.assertTrue(any("(que que CS -)" in line for line in lines))

        lines = self.parser.parse("El Senado aprobó la ley que había propuesto el gobierno.")
        self.assertTrue("subord-rel" in labels(lines))
        self.assertTrue(any("(que que PR0CN000 -)" in line for line in lines))

    def test_quotes(self):
        # textualCite / quoteFinder: a sentence opening with a quote has an F-no-c root
        lines = self.parser.parse('"Vamos a ganar", afirmó el ministro.')
        self.assertEqual("F-no-c_[", lines[0])

    def test_dates_contractions_and_named_entities(self):
        lines = self.parser.parse("El presidente Mauricio Macri llegó del sur el 3 de mayo de 2015.")
        joined = "\n".join(lines)
        self.assertTrue("(Mauricio_Macri mauricio_macri NP00SP0 -)" in joined)
        self.assertTrue("(de de SPS00 -)" in joined and "(el el DA0MS0 -)" in joined)
        self.assertTrue("[??:3/5/2015:??.??:??] W -)" in joined)
        self.assertTrue("data" in labels(lines))

    def test_language_detection(self):
        detector = LanguageDetectorClient()
        self.assertTrue(detector.health_check())
        self.assertEqual("es", detector.parse("El presidente llegó ayer a la ciudad de Buenos Aires.")[0])


if __name__ == '__main__':
    unittest.main()
