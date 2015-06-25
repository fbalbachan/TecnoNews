# -*- coding: utf-8 -*-

from src.model.output.paragraphEntityTagger import ParagraphEntityTagger
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.referent.entityUnifier import EntityUnifier
from src.model.referent.referentInformationExtractor import ReferentInformationExtractor
from src.model.referent.referentSentimentalScorer import ReferentSentimentalScorer
from src.sentiment.sentimentalSummarizer import SentimentalSummarizer


class Sentilecto:
    def __init__(self):
        pass

    @staticmethod
    def analyze(text):
        if type(text) == unicode:
            text = text.encode("utf-8")  # unicode -> str (utf8-encoded)

        analysis = {}

        analyzer = ParagraphAnalyzer()
        paragraph = Paragraph.from_text(text)

        analyzer.analyze(paragraph)

        analysis["paragraph"] = paragraph
        analysis["summary"] = SentimentalSummarizer(paragraph).analyze()

        EntityUnifier(paragraph).unify()
        ReferentInformationExtractor.update_named_referents_of(paragraph)

        analysis["referent_scoring"] = ReferentSentimentalScorer(paragraph).score()

        tagged_text, tag_mapping = ParagraphEntityTagger().tag_all(paragraph, "span")
        analysis["tagged_text"] = tagged_text
        analysis["tag_mapping"] = tag_mapping

        return analysis
