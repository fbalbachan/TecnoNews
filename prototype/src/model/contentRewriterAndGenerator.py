# -*- coding: utf-8 -*-
from src.extension.textInserter import TextInserter
from src.extension.wikipediaContentGenerator import WikipediaContentGenerator
from src.model.referent.referentRanker import ReferentRanker
from src.model.sentilecto import Sentilecto
from src.rewrite.rewriter import Rewriter


class ContentRewriterAndGenerator:

    def run(self, text):
        changed = text
        analysis = self._analyze(changed)
        analysis["referent_ranking"] = ReferentRanker(analysis["paragraph"]).rank()

        analysis["generated_content_wiki"] = WikipediaContentGenerator(analysis).generate()

        # TODO: Modifications to adapt Sentilecto's Demo to changes in code introduced for tecnonews
        # text_inserter = TextInserter(analysis)
        # changed = text_inserter.get()

        for referent, content, page in analysis["generated_content_wiki"]:
            if not isinstance(content, unicode):
                content = unicode(content, 'utf-8')
            changed = changed + u"\n" + content

        analysis = self._analyze(changed)
        rewriter = Rewriter(analysis['paragraph'])
        changed = rewriter.rewrite()

        return { "source" : text, "changed" : changed }

    def _analyze(self, text):
        return Sentilecto().analyze(text)
