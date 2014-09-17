#-*- coding: utf-8 -*-
from Levenshtein import jaro_winkler
from re import sub
from wikipedia.exceptions import DisambiguationError

from src.model.paragraph.paragraph import Paragraph
from src.model.referent.referentInformationExtractor import ReferentInformationExtractor
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
                summary = wk.page(page_rank[0]).summary
            except DisambiguationError:
                print "(!) La página '", page_rank[0], "' llevaba a una página de desambiguación"

                summary = self.disambiguated_summary_for(referent)
                if not summary: continue

            summary = summary.encode("utf-8")

            print "\n[Summary de wikipedia para", page_rank[0], "]\n"
            print summary
            print "--\n"

            paragraph = Paragraph.from_text(self.without_parentheses(summary))
            sentence = paragraph.sentences[0]

            print "Primer oración:", sentence.text

            break

    def disambiguated_summary_for(self, referent):
        print "[Intentando desambiguar", referent.name(), "con info adicional:", referent.extra_words, "]"

        if len(referent.extra_words) < 2: return

        pages = wk.search(" ".join(referent.extra_words), results = 1)
        if not pages: return

        page = pages[0]

        page_words = set([ word.lower().encode("utf-8") for word in page.split() ])
        referent_words = set(referent.extra_words)

        jaccard_index = len(page_words & referent_words) / float(len(page_words | referent_words))

        print "\tWikipage:", page, "- jaccard_index", jaccard_index
        if jaccard_index >= 0.5: return wk.page(pages[0]).summary

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