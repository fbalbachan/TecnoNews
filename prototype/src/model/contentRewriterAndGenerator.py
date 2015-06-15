# -*- coding: utf-8 -*-
from src.extension.wikipediaContentGenerator import WikipediaContentGenerator
from src.model.referent.referentRanker import ReferentRanker
from src.model.sentilecto import Sentilecto
from src.rewrite.rewriter import Rewriter

debug_mode = False


class ContentRewriterAndGenerator:

    def __init__(self):
        pass

    def run(self, text):
        if debug_mode: print "--> ContentRewriterAndGenerator.run()"
        changed = text
        analysis = self._analyze(changed)
        analysis["referent_ranking"] = ReferentRanker(analysis["paragraph"]).rank()
        analysis["generated_content_wiki"] = WikipediaContentGenerator(analysis).generate()

        for referent, content, page in analysis["generated_content_wiki"]:
            if not isinstance(content, unicode):
                content = unicode(content, 'utf-8')
            changed = changed + u"\n" + content

        analysis = self._analyze(changed)
        rewriter = Rewriter(analysis['paragraph'])
        changed = rewriter.rewrite()

        if debug_mode: print "<-- ContentRewriterAndGenerator.run() - changed: ", changed, "\n\n"
        return {"source": text, "changed": changed}

    def _analyze(self, text):
        if debug_mode: print "--> ContentRewriterAndGenerator._analyze()"
        return Sentilecto().analyze(text)
