# -*- coding: utf-8 -*-

from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.sentiment.sentimentalSummarizer import SentimentalSummarizer


class Sentilecto:
    def analyze(self, text):
        if type(text) == unicode: input_text = text.encode("utf-8") # unicode -> str (encoded)

        analysis = {}

        analyzer = ParagraphAnalyzer()
        paragraph = Paragraph.from_text(input_text)
        analyzer.analyze(paragraph)

        analysis["paragraph"] = paragraph
        analysis["summary"] = SentimentalSummarizer(paragraph).analyze()

        return analysis