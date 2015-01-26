__author__ = 'Pablo Perez De Angelis'

from src.utils.textDistance import TextDistance
import numpy

related_logger = None

class SimilarParagraph:
    def __init__(self, newsEntry, other_versions):
        self.text_distance = TextDistance()
        self.news = newsEntry
        print self.news.content
        self.paragraphs = self.get_paragraphs(self.news.content)
        self.load_other_sources(other_versions)
        from pprint import pprint
        print pprint(self.paragraphs)
        print pprint(self.paragraph_c1)
        print pprint(self.paragraph_c2)

    @staticmethod
    def get_logger():
        global related_logger
        if not related_logger:
            import logging
            from logging.handlers import RotatingFileHandler
            import logging.handlers

            logging.basicConfig(level=logging.INFO, format='%(message)s')

            logger = logging.getLogger('Related News')
            logger.addHandler(RotatingFileHandler('logs/paragraph.log', 'a',
                maxBytes=5000000, backupCount=50))
            logger.addHandler(logging.StreamHandler())
            logger.propagate = False
            related_logger = logger
        return related_logger

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
            print "\tcomparing paragraph %d of t0_paragraphs" % k
            t1_k = self._paragraphSimilarity(t0_paragraphs[k], paragraph_l)
            print "\t", t1_k
            if t1_k > max_similarity or max_idx == -1:
                max_idx = k
                max_similarity = t1_k

        return max_idx, max_similarity

    def less_similar_paragraph(self, t0_paragraphs, t1_paragraphs):
        """
        t0_paragraph dictionary of paragraph
        t1_paragraph dictionary of paragraph
        return a (similarity, idx) where key is the key in t1_paragraphs
        of the less similar paragraph off all the paragraph in t1_paragraphs
        compared with all the paragraphs of t0_paragraphs
        """
        min_simil = 0
        min_simil_idx = -1
        simil_idx = -1

        for k in t1_paragraphs.keys():
            print "paragraph %d of t1_paragraphs" % k
            simil_idx, simil_k = self.max_similarity_of_paragraph_l(t0_paragraphs, t1_paragraphs[k])
            if simil_k < min_simil or min_simil_idx == -1:
                min_simil = simil_k
                min_simil_idx = k

        return min_simil, min_simil_idx, simil_idx


    # TODO: Refactor create 2 methods
    # insert_paragraph return Bool
    #  try to insert paragraph
    # get_content_after_insert the result of insert paragraph content
    def get_content_after_insert(self):
        if not self.paragraphs:
            return self.paragraphs, False

        simil, t1_p, t0_p = self.less_similar_paragraph(self.paragraphs, self.paragraph_c1)

        content = ''
        for key in self.paragraphs.keys():
            print self.paragraphs[key]
            content += '\n' + self.paragraphs[key]
            if key == t0_p:
                print ">>>"
                print self.paragraph_c1[t1_p]
                content += '\n' + self.paragraph_c1[t1_p]
                print ">>>"

        return content

def test_news1_news2():
    sp = SimilarParagraph([], [])
    t0 = open('news1_0', 'r').read()
    t1 = open('news1_1', 'r').read()
    t0 = unicode(t0, 'utf-8')
    t1 = unicode(t1, 'utf-8')
    t0_paragraphs = sp.get_paragraphs(t0)
    t1_paragraphs = sp.get_paragraphs(t1)
    simil, t1_p, t0_p = sp.less_similar_paragraph(t0_paragraphs, t1_paragraphs)

    for key in t0_paragraphs.keys():
        print t0_paragraphs[key]
        if key == t0_p:
            print ">>>"
            print t1_paragraphs[t1_p]
            print ">>>"


if __name__ == '__main__':
    test_news1_news2()
