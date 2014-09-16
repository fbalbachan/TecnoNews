#-*- coding: utf-8 -*-
from Levenshtein import jaro_winkler
from re import sub
from wikipedia.exceptions import DisambiguationError

from src.model.paragraph.paragraph import Paragraph
import wikipedia as wk


class WikipediaContentGenerator:
    def __init__(self, analysis):
        self.analysis = analysis

    def generate(self):
        wk.set_lang("es")
        ranking = self.analysis["referent_ranking"]

        ranking = filter(lambda (referent, score): bool(referent.semantic_classification()), ranking)

        print "[Ranking de referentes]"
        for referent, score in ranking:
            print "\t", referent, "->", score
        print

        for referent, score in ranking[0:2]:  # @UnusedVariable
            page_rank = self.page_rank_for(referent)
            if not page_rank:
                print "(!) El referente", referent.name(), "no tiene resultados aceptables en Wikipedia"
                continue

            try:
                summary = wk.page(page_rank[0]).summary.encode("utf-8")
            except DisambiguationError:
                print "(!) La página '", page_rank[0], "' llevaba a una página de desambiguación"
                continue

            print "\n[Summary de wikipedia para", page_rank[0], "]\n"
            print summary
            print "--\n"

            paragraph = Paragraph.from_text(self.without_parentheses(summary))
            sentence = paragraph.sentences[0]

            print "Primer oración:", sentence.text

            break

    def without_parentheses(self, text):
        text = sub("\([^)]*\)", "", text)
        text = sub(" +", " ", text)
        text = text.replace(" ,", ",")
        return text

    def page_rank_for(self, referent):
        name = referent.name()

        print "\nRanking de páginas para referente", name

        pages = [ page.encode("utf-8") for page in wk.search(name, results = 3) ]
        page_rank = [ (page, jaro_winkler(page, name)) for page in pages ]

        for page, rank in page_rank:
            print "\t",  page, "->", rank

        return [ page for page, rank in page_rank if rank > 0.9 ]