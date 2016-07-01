# -*- coding: utf-8 -*-


class TextInserter:
    def __init__(self, analysis):
        self.analysis = analysis
        self.text = self.analysis["paragraph"].text
        self.paragraphs = self.get_paragraphs()
        self.paragraph_indexes = self.compute_paragraph_indexes()

    def get_paragraphs(self):
        return [paragraph for paragraph in self.text.split("\n") if paragraph != '']

    def get(self):
        injections_wiki = self.get_injections_wiki_idx()
        print "TextInserter: Injections_wiki", injections_wiki, "\n"
        injections_paragraphs = self.get_injection_paragraphs_other_sources()
        generated = u""

        injected_count = 0  # keep the count of how many paragraph we add to the news
        wiki_injected = False
        #raconto_available = self.analysis["raconto_content"] is not None
        raconto_available = False

        for idx, paragraph in enumerate(self.paragraphs):
            if not isinstance(paragraph, unicode):
                paragraph = unicode(paragraph, 'utf-8')
                # TODO: Transform all to unicode at the beginning of the pipeline!!!
            generated += paragraph + u'\n'

            # if there is some paragraph to append
            if idx in injections_paragraphs.keys():
                injected_count += 1
                # generated += u'[eyesonly logged="in"]' \
                #              + u'<p><strong>Start paragraph from other coverage</strong></p>[/eyesonly]'
                generated += u'\n' + injections_paragraphs[idx] + u'\n'
                if raconto_available:
                    raconto_available = False
                    generated += self.analysis["raconto_content"] + u'\n'
                # generated += u'[eyesonly logged="in"]' \
                #              + u'<p><strong> Ends paragraph from other coverage<strong></p>[/eyesonly]'

            if idx in injections_wiki.keys():
                wiki_injected = True
                for content in injections_wiki[idx]:
                    # generated += u'[eyesonly logged="in"]' \
                    #              + u'<p><strong>Starts paragraph from wiki</strong></p> [/eyesonly]\n'
                    generated += u'\n' + content + u'\n'
                    # generated += u'[eyesonly logged="in"]' \
                    #              + u'<p><strong>Ends paragraph from wiki</strong></p>[/eyesonly]'

        if wiki_injected:        # TODO: validate experiment and remove code
            injected_count += 0  # EXPERIMENT: We didn't take in count wiki as injected paragraph
                                 # it affects the number of news we publish.

        return injected_count, generated.strip()

    def get_injections_wiki_idx(self):
        injections = {}

        contents = self.analysis["generated_content_wiki"]

        print "TextInserter: Generated Wikipedia contents"
        for c in contents:
            print c
        print "--------"

        for referent, content, page in contents[0:2]:  # @UnusedVariable
            referent_index = referent.first_occurrence().token.start()
            previous_paragraph_idx = self.idx_paragraph_of(referent_index)

            if previous_paragraph_idx not in injections:
                injections[previous_paragraph_idx] = []

            # TODO: Transform all to unicode at the beginning of the
            # pipeline!!!
            if not isinstance(content, unicode):
                content = unicode(content, 'utf-8')

            injections[previous_paragraph_idx].append(content)

        return injections

    def get_injection_paragraphs_other_sources(self):
        return self.analysis["generated_content_other_sources"]

    def paragraph_of(self, index):
        for paragraph in self.paragraphs:
            start, end = self.paragraph_indexes[paragraph]
            if start <= index < end:
                return paragraph

    def idx_paragraph_of(self, index):
        paragraph_idx = None

        for idx, paragraph in enumerate(self.paragraphs):
            start, end = self.paragraph_indexes[paragraph]
            if start <= index < end:
                paragraph_idx = idx
                break

        return paragraph_idx

    def compute_paragraph_indexes(self):
        paragraph_indexes = {}
        for paragraph in self.paragraphs:
            start = self.text.index(paragraph)
            paragraph_indexes[paragraph] = (start, start + len(paragraph))
        return paragraph_indexes
