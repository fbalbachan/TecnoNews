# -*- coding: utf-8 -*-

from src.model.output.paragraphEntityTagger import ParagraphEntityTagger
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.referent.entityUnifier import EntityUnifier
from src.model.referent.referentInformationExtractor import ReferentInformationExtractor
from src.model.referent.referentSentimentalScorer import ReferentSentimentalScorer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.sentiment.sentimentalSummarizer import SentimentalSummarizer
from src.utils.fact_time_utils import FactTimeUtils


class Sentilecto:
    def __init__(self):
        pass

    @staticmethod
    def analyze(text, output_demo_debug=False):

        analysis = {}
        analysis["global_context"] = {"TEST":"TEST1"}

        paragraph = Paragraph.from_text(text)
        sentence_analyzer = SentenceAnalyzer(global_context=analysis["global_context"])
        paragraph_analyzer = ParagraphAnalyzer(sentence_analyzer, output_demo_debug)

        paragraph_analyzer.analyze(paragraph)
        analysis["paragraph"] = paragraph

        analysis["summary"] = SentimentalSummarizer(paragraph).analyze()

        EntityUnifier(paragraph).unify()
        ReferentInformationExtractor.update_named_referents_of(paragraph)

        analysis["referent_scoring"] = ReferentSentimentalScorer(paragraph).score()

        tagged_text, tag_mapping = ParagraphEntityTagger().tag_all(paragraph, "span")
        analysis["tagged_text"] = tagged_text
        analysis["tag_mapping"] = tag_mapping

        FactTimeUtils().set_analysis_time_reference(analysis)

        return analysis
