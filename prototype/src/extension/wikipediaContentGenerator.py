#-*- coding: utf-8 -*-
from Levenshtein import jaro_winkler
from re import sub
from wikipedia.exceptions import DisambiguationError

from src.model.paragraph.paragraph import Paragraph
from src.utils.resources import instance as resources
import wikipedia as wk

from src.utils.genderDetection.genderDetector import load_name_lists
from src.utils.configProvider import ConfigProvider
from src.utils.csvwrapper import unicode_csv_reader
from unidecode import unidecode

class WikipediaContentGenerator:
    def __init__(self, analysis):
        self.analysis = analysis

    def generate(self):
        wk.set_lang("es")
        ranking = self.analysis["referent_ranking"]
        ranking = filter(lambda (referent, score): not self.is_blacklisted(referent), ranking)
        ranking = filter(lambda (referent, score): not self.is_name_blacklisted(referent), ranking)

        content = []

        for referent, score in ranking[0:3]:  # @UnusedVariable
            content_and_page = self.content_and_page_for(referent)
            if content_and_page:
                sentence_text, page = content_and_page
                content.append((referent, sentence_text, page))
                if len(content) > 1:
                    break
        return content

    def is_name_blacklisted(self, referent):
        def has_blacklisted_name(entity):
            formated_entity = unidecode(entity.lexical_form.decode("utf-8"))
            return formated_entity.upper() in self.names or formated_entity.lower() in self.countries_list

        return any((has_blacklisted_name(reference) for reference in referent.explicit_references() ))

    def is_blacklisted(self, referent):
        def has_blacklisted_word(entity):
            #return any((black_word in entity.lexical_form for black_word in self.black_words ))
            return entity.lexical_form in self.black_words or str(entity.kernel) in self.black_words
        return any((has_blacklisted_word(reference) for reference in referent.explicit_references() ))

    def content_and_page_for(self, referent):
        page_rank = self.page_rank_for(referent)
        tokens = [unidecode(a_token.decode("utf-8")).lower() for a_token in referent.name().split()]

        if not page_rank:
            return

        try:
            page = wk.page(page_rank[0])
        except DisambiguationError:
            page = self.disambiguated_page_for(referent)
            if not page:
                return

        if any(a_token not in unidecode(page.summary).lower() for a_token in tokens):
            return

        summary = page.summary.encode("utf-8")

        try:
            sentence = self.first_content_sentence_of(summary)
        except StopIteration:
            return

        content = sentence.text
        if content[-1] != ".":
            content += "."

        return content, page

    def first_content_sentence_of(self, summary):
        paragraph = Paragraph.from_text(self.without_parentheses(summary))
        return iter((sentence for sentence in paragraph.sentences if self.is_valid_sentence(sentence))).next()

    def is_valid_sentence(self, sentence):
        text = sentence.text.lower()
        if len(text.split()) < 10:
            return False

        return not (("redirigen" in text or "redirige" in text) and ("véase" in text or "desambiguación" in text))

    def disambiguated_page_for(self, referent):
        if len(referent.extra_words) < 2:
            return

        pages = wk.search(" ".join(referent.extra_words), results=1)
        if not pages:
            return

        page = pages[0].encode("utf-8")

        page_words = set([word.lower() for word in page.split()])
        referent_words = set(referent.extra_words)

        jaccard_index = len(page_words & referent_words) / float(len(page_words | referent_words))

        if jaccard_index >= 0.5:
            return wk.page(pages[0])

    def without_parentheses(self, text):
        text = sub("\([^)]*\)", "", text, )
        text = sub(" +", " ", text)
        text = text.replace(" ,", ",")
        return text

    def page_rank_for(self, referent):
        name = referent.name()

        pages = [page.encode("utf-8") for page in wk.search(name, results=3)]
        page_rank = [(page, jaro_winkler(page, name)) for page in pages]

        return [page for page, rank in page_rank if rank > 0.93]

    black_words = resources.parse_csv_in("rewrite", "blacklist")

    config = ConfigProvider()
    names = load_name_lists()
    names = names["male"].union(names["female"]).union(names["neutral"])
    countries_file = config.get("resources", "countries")
    countries_reader = unicode_csv_reader(open(countries_file, 'r'), first_line_is_header=False, delimiter=',')
    countries_list = [unicode(country[0].lower(), 'utf-8') for country in countries_reader]
