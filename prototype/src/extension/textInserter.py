# -*- coding: utf-8 -*-

class TextInserter:
    def __init__(self, analysis):
        self.analysis = analysis
        self.text = self.analysis["paragraph"].text
        self.paragraphs = self.text.split("\n")
        self.paragraph_indexes = self.compute_paragraph_indexes()

    def get(self):
        injections_wiki = self.get_injections_wiki()
        injections_paragraphs = self.get_injection_paragraphs_other_sources()
        generated = u""

        for idx, paragraph in enumerate(self.paragraphs):
            if not isinstance(paragraph, unicode):
                paragraph = unicode(paragraph, 'utf-8')
                # TODO: Transform all to unicode at the beginning of the
                # pipeline!!!
            generated += paragraph + u"\n"

            # if there is some paragraph to append
            if idx in injections_paragraphs.keys():
                generated += injections_paragraphs[idx]

            #TODO: may use idx por para todo
            if paragraph in injections_wiki:
                for content in injections_wiki[paragraph]:
                    generated += content + "\n"

        return generated.strip()

    def get_injections_wiki(self):
        injections = {}

        contents = self.analysis["generated_content_wiki"]

        for c in contents: print c
        print "--"

        for referent, content, page in contents[0:2]:  # @UnusedVariable
            referent_index = referent.first_occurrence().token.start()
            previous_paragraph = self.paragraph_of(referent_index)
            if previous_paragraph not in injections: injections[previous_paragraph] = []
            injections[previous_paragraph].append(content)
        return injections

    def get_injection_paragraphs_other_sources(self):
        return self.analysis["generated_content_other_sources"]

    def paragraph_of(self, index):
        for paragraph in self.paragraphs:
            start, end = self.paragraph_indexes[paragraph]
            if index >= start and index < end: return paragraph

    def compute_paragraph_indexes(self):
        paragraph_indexes = {}
        for paragraph in self.paragraphs:
            start = self.text.index(paragraph)
            paragraph_indexes[paragraph] = (start, start + len(paragraph))
        return paragraph_indexes