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

        for r in ranking: print "*", r
        print

        for referent, score in ranking[0:2]:  # @UnusedVariable
            print "Analizando:", referent
            content = self.content_for(referent)
            if content: return content

    def content_for(self, referent):
        page_rank = self.page_rank_for(referent)
        if not page_rank:
            print "(!) No hay resultados aceptables"
            return

        try:
            summary = wk.page(page_rank[0]).summary
        except DisambiguationError:
            print "(!) Desambiguación"

            summary = self.disambiguated_summary_for(referent)
            if not summary: return

        summary = summary.encode("utf-8")

        sentence = self.first_content_sentence_of(summary)
        print "Contenido:", sentence.text
        return sentence.text

    def first_content_sentence_of(self, summary):
        paragraph = Paragraph.from_text(self.without_parentheses(summary))
        return iter(( sentence for sentence in paragraph.sentences if self.is_valid_sentence(sentence))).next()

    def is_valid_sentence(self, sentence):
        text = sentence.text.lower()
        if len(text.split()) < 10: return False
        return not (("redirigen" in text or "redirige" in text) and ("véase" in text or "desambiguación" in text))

    def disambiguated_summary_for(self, referent):
        if len(referent.extra_words) < 2: return

        pages = wk.search(" ".join(referent.extra_words), results = 1)
        if not pages: return

        page = pages[0].encode("utf-8")

        page_words = set([ word.lower() for word in page.split() ])
        referent_words = set(referent.extra_words)

        jaccard_index = len(page_words & referent_words) / float(len(page_words | referent_words))

        if jaccard_index >= 0.5: return wk.page(pages[0]).summary

    def without_parentheses(self, text):
        text = sub("\([^)]*\)", "", text, )
        text = sub(" +", " ", text)
        text = text.replace(" ,", ",")
        return text

    def page_rank_for(self, referent):
        name = referent.name()

        pages = [ page.encode("utf-8") for page in wk.search(name, results = 3) ]
        page_rank = [ (page, jaro_winkler(page, name)) for page in pages ]

        return [ page for page, rank in page_rank if rank > 0.9 ]