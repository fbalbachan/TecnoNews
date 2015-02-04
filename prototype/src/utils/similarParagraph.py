__author__ = 'Pablo Perez De Angelis'

from src.utils.textDistance import TextDistance
from collections import defaultdict

paragraph_logger = None

class SimilarParagraph:
    def __init__(self, analysis, other_versions):
        self.get_logger()
        self.analysis = analysis
        self.text_distance = TextDistance()
        self.text = self.analysis["paragraph"].text
        if not isinstance(self.text, unicode):
            paragraph_logger.error('analysis["paragraph"].text is not unicode')
            paragraph_logger.error('decoding analysis["paragraph"].text to unicode')
            self.text = unicode(self.text, 'utf-8')
        self.paragraphs = self.get_paragraphs(self.text)
        self.load_other_sources(other_versions)
        self.clean_candidate_paragraphs()
        self.paragraphs_selected = defaultdict(lambda: '')

    @staticmethod
    def get_logger():
        global paragraph_logger
        if not paragraph_logger:
            import logging
            from logging.handlers import RotatingFileHandler
            import logging.handlers

            logging.basicConfig(level=logging.INFO, format='%(message)s')

            logger = logging.getLogger('Related News')
            logger.addHandler(RotatingFileHandler('logs/paragraph.log', 'a',
                maxBytes=5000000, backupCount=50))
            logger.addHandler(logging.StreamHandler())
            logger.propagate = False
            paragraph_logger = logger
        return paragraph_logger

    def _paragraphSimilarity(self, firstParagraph, secondParagraph):

        similarity = self.text_distance.similarity(firstParagraph, secondParagraph)

        return similarity

    def get_paragraphs(self, text):
        """
        @param text string
        returns a dictionary with {numberOfParagraph:paragraph} WO emtpy ones
        """
        return {idx: paragraph for (idx, paragraph)
                in enumerate(text.split('\n')) if paragraph != ''}

    def load_other_sources(self, other_news):

        if len(other_news) > 1:
            self.paragraph_c1 = self.get_paragraphs(other_news[0].content)
            self.paragraph_c2 = self.get_paragraphs(other_news[1].content)
        elif len(other_news) == 1:
            self.paragraph_c1 = self.get_paragraphs(other_news[0].content)
            self.paragraph_c2 = {}
        else:
            self.paragraph_c1 = {}
            self.paragraph_c2 = {}

    def clean_candidate_paragraphs(self):
        self.delete_invalid_candidate_paragraph(self.paragraph_c1)
        self.delete_invalid_candidate_paragraph(self.paragraph_c2)

    def delete_invalid_candidate_paragraph(self, paragraphs):
        for key in paragraphs.keys():
            if '@' in paragraphs[key]:
                del paragraphs[key]

    def max_similarity_of_paragraph_l(self, t0_paragraphs, paragraph_l):
        """
        t1_paragraph dict of paragraphs
        paragraph_l paragraph we search for the the max similarity
        returns the (idx, similarity) of the p_j in t1_paragraphs / similarity(p_j, paragraph_l)
        >= similarity(p_k, paragraph_l) for k in tq_paragraph
        """
        max_similarity = 0
        max_idx = -1

        for k in t0_paragraphs.keys():
            paragraph_logger.info("\tcomparing paragraph %d of t0_paragraphs" % k)
            t1_k = self._paragraphSimilarity(t0_paragraphs[k], paragraph_l)
            paragraph_logger.info("\t %s" % t1_k)
            if t1_k > max_similarity or max_idx == -1:
                max_idx = k
                max_similarity = t1_k

        return max_idx, max_similarity

    def less_similar_paragraph(self, t0_paragraphs, t1_paragraphs):
        """
        t0_paragraph dictionary of paragraph
        t1_paragraph dictionary of paragraph
        return a (min_simil, min_simil_idx, t0_max_simil_idx_of_t1_min)
        where
            min_simil: is the minimal similarity,
            min_simil_idx: is the index of the less similar paragraph off all the paragraph in t1_paragraphs
            compared with all the paragraphs of t0_paragraphs
            t0_max_simil: is the idx of a paragraph in t0_paragraphs which is the more similar
            paragraph to t1_paragraphs[min_simil_idx]

        """
        min_simil = 0
        min_simil_idx = -1
        t0_max_simil = -1

        for k in t1_paragraphs.keys():
            paragraph_logger.info("paragraph %d of t1_paragraphs" % k)
            simil_idx, simil_k = self.max_similarity_of_paragraph_l(t0_paragraphs, t1_paragraphs[k])

            if simil_k > 0 and (simil_k < min_simil or min_simil_idx == -1):
                min_simil = simil_k
                min_simil_idx = k
                t0_max_simil = simil_idx

        return min_simil, min_simil_idx, t0_max_simil

    # TODO: Remove injection_mark after betha testing is over
    def select_paragraph(self, simil, t1_p, t0_p, paragraphs, injection_mark):

        if t1_p != -1:
            paragraph_logger.info("\nselected paragraph: %s" % t1_p)
            paragraph_logger.info(paragraphs[t1_p])
            self.add_result_paragraph(t0_p, paragraphs[t1_p], injection_mark)
            del paragraphs[t1_p]

    def add_result_paragraph(self, idx, paragraph, injection_mark):
        self.paragraphs_selected[idx] += injection_mark + paragraph + injection_mark

    def get_generated_content(self):

        paragraph_logger.info("numered paragraphs\n")
        paragraph_logger.info("Original:\n")
        paragraph_logger.info(self.paragraphs)
        paragraph_logger.info("\nFirst other cover\n")
        paragraph_logger.info(self.paragraph_c1)
        paragraph_logger.info("\nSecond other cover\n")
        paragraph_logger.info(self.paragraph_c2)

        paragraph_logger.info("----------------")
        # First paragraph from paragraph_c1
        simil, t1_p, t0_p = self.less_similar_paragraph(self.paragraphs, self.paragraph_c1)
        paragraph_logger.info("%s, %s, %s" % (simil, t1_p, t0_p))
        injection_mark = u""

        self.select_paragraph(simil, t1_p, t0_p, self.paragraph_c1, injection_mark)
        assert t1_p not in self.paragraph_c1

        paragraph_logger.info("--------------\n")
        # Second paragraph from paragraph_c1
        simil, t1_p, t0_p = self.less_similar_paragraph(self.paragraphs, self.paragraph_c1)
        paragraph_logger.info("%s, %s, %s" % (simil, t1_p, t0_p))

        injection_mark = u""
        self.select_paragraph(simil, t1_p, t0_p, self.paragraph_c1, injection_mark)
        assert t1_p not in self.paragraph_c1

        paragraph_logger.info("--------------\n")
        # First paragraph from paragraphs_c2
        simil, t1_p, t0_p = self.less_similar_paragraph(self.paragraphs, self.paragraph_c2)

        injection_mark = u""
        self.select_paragraph(simil, t1_p, t0_p, self.paragraph_c2, injection_mark)
        assert t1_p not in self.paragraph_c2

        paragraph_logger.info("--------------\n")
        paragraph_logger.info("\ngenerated %s" % self.paragraphs_selected)

        return self.paragraphs_selected


def test_news1_news2():

    class MockParagraph:
        def __init__(self, text = u""):
            self.text = text
    class MockEntity:
        def __init__(self, content):
            self.content = content

    t0 = open('test_0', 'r').read()
    t1 = open('test_1', 'r').read()
    t0 = unicode(t0, 'utf-8')
    t1 = unicode(t1, 'utf-8')
    analysis = {"paragraph": MockParagraph(text=t0)}

    sp = SimilarParagraph(analysis, [MockEntity(t1)])
    print sp.paragraphs
    print sp.paragraph_c1
    print "\n"

    sp.get_generated_content()
    # t0_paragraphs = sp.get_paragraphs(t0)
    # t1_paragraphs = sp.get_paragraphs(t1)
    # simil, t1_p, t0_p = sp.less_similar_paragraph(t0_paragraphs, t1_paragraphs)
    #
    # for key in t0_paragraphs.keys():
    #     print t0_paragraphs[key]
    #     if key == t0_p:
    #         print ">>>"
    #         print t1_paragraphs[t1_p]
    #         print ">>>"


if __name__ == '__main__':
    test_news1_news2()
