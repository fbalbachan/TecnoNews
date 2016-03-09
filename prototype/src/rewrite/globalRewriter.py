# -*- coding: utf-8 -*-
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.paragraph.paragraph import Paragraph
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.model.referent.entityUnifier import EntityUnifier

debug_mode = False

class GlobalRewriter:
    def __init__(self, paragraph, ontology=None, strategies=None, clauses_for_replacements=None):
        sentenceAnalyzer = SentenceAnalyzer()
        self.analyzer = ParagraphAnalyzer(sentenceAnalyzer)
        self.paragraph = paragraph


    def rewrite(self):
        text = self.paragraph.text
        self.paragraph = Paragraph.from_text(text)
        self.analyzer.analyze(self.paragraph)
        EntityUnifier(self.paragraph).unify()

        sentences_entity_context = []

        for a_sentence in self.paragraph.sentences:
            if debug_mode: print "-->SENTENCE:" + a_sentence.text

            a_clause = a_sentence.main_clause()

            if debug_mode: print "---->CLAUSE: " + str(a_clause)
            if debug_mode: print "\n------>" + str(a_clause.all_entities()) + "\n"

            sentences_entity_context.append(a_clause.named_entities_by_structure())


        while sentences_entity_context:
            main_sentence_idx = len(self.paragraph.sentences) - len(sentences_entity_context)

            #GET ALL ENTITIES WITH THEIR RESPECTIVE ROLES:
            current_context = sentences_entity_context.pop(0)
            current_entities = {str(k):{"entity_object":k,"role":v} for (k,v) in current_context.iteritems() if not k.appositions}

            #LOOP THROUGH ALL FOLLOWING SENTENCES:
            for current_idx, a_following_context in enumerate(sentences_entity_context):
                #Only search 5 sentences ahead
                if current_idx > 5:
                    break

                secondary_sentence_idx = main_sentence_idx + current_idx + 1

                #GET AL ENTITIES WITH SUBJECT ROLE:
                subject_entities = [k for (k,v) in a_following_context.iteritems() if v == u'subject']

                for a_subject_entity in subject_entities:
                    #GOTO REFERENCE (IF NECESSARY)
                    dereferenced_entity = a_subject_entity.referent.designated_ref()

                    #IF MAIN SENTENCE CONTAINS THIS ENTITY AND SECONDARY DOESNT CONTAIN APPOSITIONS:
                    if str(dereferenced_entity) in current_entities and not a_subject_entity.appositions:

                        main_role = current_entities[str(dereferenced_entity)]["role"]
                        main_entity = current_entities[str(dereferenced_entity)]["entity_object"]
                        main_sentence = self.paragraph.sentences[main_sentence_idx]

                        secondary_sentence = self.paragraph.sentences[secondary_sentence_idx]
                        secondary_entity = a_subject_entity

                        #NEED UNICODE FOR SLICING!!
                        input_paragraph = self.paragraph.text.decode('utf-8')

                        if debug_mode: print "----------HAY CAMBIO----------"
                        if debug_mode: print "---Role: " + main_role.encode('utf-8')
                        if debug_mode: print "---Main sentence: " + main_sentence.text
                        if debug_mode: print "---Secondary sentence: " + secondary_sentence.text
                        if debug_mode: print "\n"

                        #Extract sentence:
                        new_secondary = input_paragraph[secondary_sentence.token.start():secondary_sentence.token.end()]

                        #Remove entity
                        if not secondary_entity.is_tacit():
                            new_secondary = new_secondary[secondary_entity.token.end()-secondary_sentence.token.start():].strip()

                        if new_secondary[-1] == ".":
                            new_secondary = new_secondary[:-1]

                        #Remove main and secondary sentences from paragraph
                        new_paragraph_after = input_paragraph[main_sentence.token.end():secondary_sentence.token.start()].strip() + input_paragraph[secondary_sentence.token.end():]
                        new_paragraph_before = input_paragraph[:main_sentence.token.start()].strip()

                        #Build new merged sentence (main+secondary)
                        new_main_before = input_paragraph[main_sentence.token.start():main_entity.token.end()]
                        new_main_after = input_paragraph[main_entity.token.end():main_sentence.token.end()]
                        new_main = new_main_before.strip() + ", que " + new_secondary + ", " + new_main_after.strip()



                        return (new_paragraph_before + " " + new_main + " " + new_paragraph_after).strip()
