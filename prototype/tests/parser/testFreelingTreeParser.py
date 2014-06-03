#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.ling.msi_mapper import tag2fullmsi
from src.parser.freelingTreeParser import FreelingTreeParser
from src.parser.labelNode import LabelNode
from src.parser.leafNode import LeafNode


class FreelingTreeParserTest(unittest.TestCase):

    def test(self):
        parser = FreelingTreeParser()
        parsed = parser.from_file("tests/parser/input/parse_tree.txt")

        grup_verb_0 = LabelNode("grup-verb")
        sn_1 = LabelNode("sn")
        grup_nom_ms_2 = LabelNode("grup-nom-ms")
        w_ms_3 = LabelNode("w-ms")
        leandro_4 = LeafNode("Leandro", "leandro", tag2fullmsi("NP00000"))
        verb_1 = LabelNode("verb")
        comio_2 = LeafNode("comió", "comer", tag2fullmsi("VMIS3S0"))
        sn2_1 = LabelNode("sn")
        espec_fs_2 = LabelNode("espec-fs")
        j_fs_3 = LabelNode("j-fs")
        la_4 = LeafNode("la", "el", tag2fullmsi("DA0FS0"))
        grup_nom_fs_2 = LabelNode("grup-nom-fs")
        n_fs_3 = LabelNode("n-fs")
        manzana_4 = LeafNode("manzana", "manzana", tag2fullmsi("NCFS000"))
        F_term_1 = LabelNode("F-term")
        dot_2 = LeafNode(".", ".", tag2fullmsi("Fp"))

        hierachy = {
                    grup_verb_0     : [sn_1, verb_1, sn2_1, F_term_1],
                    sn_1            : [grup_nom_ms_2],
                    verb_1          : [comio_2],
                    sn2_1           : [espec_fs_2, grup_nom_fs_2],
                    F_term_1        : [dot_2],
                    grup_nom_ms_2   : [w_ms_3],
                    espec_fs_2      : [j_fs_3],
                    grup_nom_fs_2   : [n_fs_3],
                    w_ms_3          : [leandro_4],
                    j_fs_3          : [la_4],
                    n_fs_3          : [manzana_4]
                    }

        for node, children in hierachy.items():
            for child in children: node.add_child(child)

        self.assertTrue(parsed.is_equivalent_to(grup_verb_0))

        self.assertListEqual(["Leandro", "comió", "la", "manzana", "."], \
                             [ leaf.original_lexical_form for leaf in parsed.leaves()])

if __name__ == '__main__':
    unittest.main()
