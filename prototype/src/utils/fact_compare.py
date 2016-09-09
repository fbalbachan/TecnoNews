# -*- coding: utf-8 -*-
from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.utils.factNormalizer import FactNormalizer
from src.utils.fact_time_utils import FactTimeUtils
import re
import datetime

class FactCompare(object):
    _ontology_parser = FreelingDictionaryParser()
    _ontology = _ontology_parser.get_ontology()
    _time_utils = FactTimeUtils()

    def __init__(self, clause1=None, clause2=None):
        self.clause1 = clause1
        self.clause2 = clause2
        self.penality_verbs = ["decir", "estar"]
        self.weights = {"subject": 1.2, "verb": 1.1, "object": 0.9, "time": 0.9}

    def compare_clause(self, clause1, clause2):
        self.clause1 = clause1
        self.clause2 = clause2
        return self.compare()

    def compare_sentence(self, sentence1, sentence2):
        short_sentence = None
        long_sentence = None

        if len(sentence1.clauses) >= len(sentence2.clauses):
            long_sentence = sentence1
            short_sentence = sentence2
        else:
            long_sentence = sentence2
            short_sentence = sentence1

        scores = []
        for a_clause1 in short_sentence.clauses:
            scores.append(0)
            for a_clause2 in long_sentence.clauses:
                score = self.compare_clause(a_clause1, a_clause2)
                if score > scores[-1]:
                    scores[-1] = score

        while len(scores) < len(long_sentence.clauses):
            scores.append(0)
        #print scores
        final_score = 0
        if len(scores) > 0:
            final_score = float(sum(scores)) / len(scores)
        #print final_score

        return final_score

    def get_boxes(self, a_fact):
        if not isinstance(a_fact, unicode):
            a_fact = a_fact.decode("utf-8")

        boxes = {"subject": None, "verb": None, "object": None, "time": None}

        halfs = a_fact.split("--TIME:")
        time = halfs[1].strip().lower()
        if time == "":
            time = None

        parts = halfs[0].split("+")
        if len(parts) < 2:
            return boxes

        boxes = {"subject": parts[0].strip(), "verb": parts[1].strip(), "object": None, "time": time}
        if len(parts) == 3:
            boxes["object"] = parts[2].strip()

        if boxes["subject"] in [u"alguien", u"algo"]:
            boxes["subject"] = u"alguien"
        elif boxes["subject"] == u"∅":
            boxes["subject"] == None

        if boxes["object"] in [u"alguien", u"algo"]:
            boxes["object"] = u"alguien"
        elif boxes["object"] == u"∅":
            boxes["object"] = None

        return boxes

    def compare_entities_data(self, referent1, referent2, msi1, msi2, equality_value):
        final_score = equality_value

        #entity1 != entity2:
        if equality_value == 0.0:

            #ref(entity1) == ref(entity2):
            if referent1 == referent2:
                final_score = 0.5
                if msi1["semantic_classification"] == msi2["semantic_classification"]:
                    final_score = 1.0

            #ref(entity1) != ref(entity2):
            else:
                if msi1["person"] == msi2["person"] and msi1["number"] == msi2["number"] and msi1["animity"] == msi2["animity"]:
                    final_score = 0.4
                else:
                    if msi1["person"] == msi2["person"]:
                        final_score = 0.1
                        if msi1["animity"] == msi2["animity"]:
                            final_score = 0.25
                    elif msi1["number"] == msi2["number"]:
                        final_score = 0.05
                        if msi1["animity"] == msi2["animity"]:
                            final_score = 0.10

        #entity1 == entity2:
        elif equality_value == 1:
            final_score = 1
            if msi1["semantic_classification"] != msi2["semantic_classification"]:
                final_score = 0.4


        return final_score

    def compare_entities(self, entity1, entity2, equality_value):
        referent1 = entity1.referent.designated_ref()
        referent2 = entity2.referent.designated_ref()
        msi1 = referent1.msi
        msi2 = referent2.msi
        return self.compare_entities_data(str(referent1), str(referent2), msi1, msi2, equality_value)


    #EXTRACTS EVERYTHING WE NEED TO KNOW TO COMPARE CLAUSES (THIS IS USEFUL FOR SAVING TO DB AND MAKE A COMPARISON WITHOUT REANALYZING)
    def extract_comparable_data(self, a_clause):
        comparable_data = {}

        a_fact = FactNormalizer(a_clause, FactCompare._ontology).fact()
        comparable_data["boxes"] = self.get_boxes(a_fact)
        comparable_data["time_reference"] = a_clause.time_reference
        comparable_data["subject_msi"] = None
        comparable_data["subject_referent"] = None
        comparable_data["verb_msi"] = None
        comparable_data["object_msi"] = None
        comparable_data["object_referent"] = None
        comparable_data["penalized_verb"] = (comparable_data["boxes"]["verb"] in self.penality_verbs)
        comparable_data["is_fact"] = a_clause.is_fact()

        if a_clause.has_structure("subject"):
            entities = a_clause.structure("subject").all_entities()
            if len(entities) > 0:
                comparable_data["subject_msi"] = entities[0].referent.designated_ref().msi
                comparable_data["subject_referent"] = str(entities[0].referent.designated_ref())

        if a_clause.verb is not None:
            comparable_data["verb_msi"] = a_clause.verb.msi

        for a_right_entity in ["od", "regimen", "equative"]:
                if a_clause.has_structure(a_right_entity):
                    entities = a_clause.structure(a_right_entity).all_entities()
                    if len(entities) > 0:
                        comparable_data["object_msi"] = entities[0].referent.designated_ref().msi
                        comparable_data["object_referent"] = str(entities[0].referent.designated_ref())

        return comparable_data

    def test_compare(self, compare_data1=None, compare_data2=None):
        if not compare_data1:
            compare_data1 = self.extract_comparable_data(self.clause1)
        if not compare_data2:
            compare_data2 = self.extract_comparable_data(self.clause2)

        if not compare_data1["is_fact"] or not compare_data2["is_fact"] or not compare_data1["verb_msi"] or not compare_data2["verb_msi"]:
            return 0

        boxes1 = compare_data1["boxes"]
        boxes2 = compare_data2["boxes"]

        time_data1 = compare_data1["time_reference"]
        time_data2 = compare_data2["time_reference"]

        equality_box = {}
        for a_label, a_value1 in boxes1.iteritems():
            equality_box[a_label] = float((boxes2[a_label] == a_value1))

        #WILDCARD
        possible_wildcard_labels = ["subject", "object"]
        for a_label in possible_wildcard_labels:
            if equality_box[a_label] == 1.0:
                if boxes1[a_label] in ["alguien", "algo", None] or boxes2[a_label] in ["alguien", "algo", None]:
                    equality_box[a_label] = -1.0
            else:
                if boxes1[a_label] in ["alguien", "algo", None] or boxes2[a_label] in ["alguien", "algo", None]:
                    equality_box[a_label] = -1.0

        if compare_data1["subject_msi"] is not None and compare_data2["subject_msi"] is not None:
            equality_box["subject"] = self.compare_entities_data(compare_data1["subject_referent"], compare_data2["subject_referent"], compare_data1["subject_msi"], compare_data2["subject_msi"], equality_box["subject"])

        if compare_data1["object_msi"] is not None and compare_data2["object_msi"] is not None:
            equality_box["object"] = self.compare_entities_data(compare_data1["object_referent"], compare_data2["object_referent"], compare_data1["object_msi"], compare_data2["object_msi"], equality_box["object"])

        #VERB:
        if equality_box["verb"] == 1.0:
            #TIME y PERSON y NUMBER
            msiScore = 0.0

            msi1 = compare_data1["verb_msi"]
            msi2 = compare_data2["verb_msi"]

            if msi1["person"] == msi2["person"]:
                msiScore = 0.75
                if msi1["number"] == msi2["number"]:
                    msiScore = 1.0
            else:
                msiScore = 0.25
                if msi1["number"] == msi2["number"]:
                    msiScore = 0.5

            equality_box["verb"] = msiScore

        if compare_data1["penalized_verb"] or compare_data2["penalized_verb"]:
            equality_box["verb"] = float(equality_box["verb"]) / 2

        #TIME:
        time_score = FactCompare._time_utils.compare_dates(compare_data1["time_reference"], compare_data2["time_reference"])
        equality_box["time"] = time_score

        #FINAL SCORE:
        available_scores = 0
        sum_scores = 0
        for a_label, a_score in equality_box.iteritems():
            if a_score > -1:
                available_scores += 1
                sum_scores += self.weights[a_label] * a_score


        final_score = 0
        if available_scores > 0:
            final_score = sum_scores/available_scores

        if final_score > 1:
            final_score = 1

        #print equality_box
        #print final_score
        return final_score


#LEGACY FUNCTION! CUANDO SE VERIFIQUE QUE LA NUEVA FUNCIONE => ELIMINAR
    def compare(self):
        if not self.clause1.is_fact() or not self.clause2.is_fact() or not self.clause1.verb or not self.clause2.verb:
            return 0

        fact1 = FactNormalizer(self.clause1, FactCompare._ontology).fact()
        fact2 = FactNormalizer(self.clause2, FactCompare._ontology).fact()

        boxes1 = self.get_boxes(fact1)
        boxes2 = self.get_boxes(fact2)

        #time_data1 = FactCompare._time_utils.extract_data_info(self.clause1)
        #time_data2 = FactCompare._time_utils.extract_data_info(self.clause2)
        time_data1 = self.clause1.time_reference
        time_data2 = self.clause2.time_reference
        #print time_data1
        #print time_data2


        equality_box = {}
        for a_label, a_value1 in boxes1.iteritems():
            equality_box[a_label] = float((boxes2[a_label] == a_value1))

        #WILDCARD
        possible_wildcard_labels = ["subject", "object"]
        for a_label in possible_wildcard_labels:
            if equality_box[a_label] == 1.0:
                if boxes1[a_label] in ["alguien", "algo", None] or boxes2[a_label] in ["alguien", "algo", None]:
                    equality_box[a_label] = -1.0
            else:
                if boxes1[a_label] in ["alguien", "algo", None] or boxes2[a_label] in ["alguien", "algo", None]:
                    equality_box[a_label] = -1.0


        #SUBJECT:
        if self.clause1.has_structure("subject") and self.clause2.has_structure("subject"):
            entities1 = self.clause1.structure("subject").all_entities()
            entities2 = self.clause2.structure("subject").all_entities()
            if len(entities1) > 0 and len(entities2) > 0:
                equality_box["subject"] = self.compare_entities(entities1[0], entities2[0], equality_box["subject"])


        #OBJECT:
        object1 = None
        object2 = None
        for a_right_entity in ["od", "regimen", "equative"]:

            if object1 is None and self.clause1.has_structure(a_right_entity):
                entities1 = self.clause1.structure(a_right_entity).all_entities()
                if len(entities1) > 0:
                    object1 = entities1[0]

            if object2 is None and self.clause2.has_structure(a_right_entity):
                entities2 = self.clause2.structure(a_right_entity).all_entities()
                if len(entities2) > 0:
                    object2 = entities2[0]

        if object1 and object2:
            equality_box["object"] = self.compare_entities(object1, object2, equality_box["object"])
        #elif not object1 and not object2:
        #    if self.clause1.has_structure("equative") and self.clause2.has_structure("equative"):
        #        if len(self.clause1.false_entities) > 0 and len(self.clause2.false_entities) > 0:
        #            fake1 = " ".join([false_entity.lemma for false_entity in self.clause1.false_entities])
        #            fake2 = " ".join([false_entity.lemma for false_entity in self.clause2.false_entities])
        #            equality_box["object"] = float(fake1 == fake2)


        #VERB:
        if equality_box["verb"] == 1.0:
            #TIME y PERSON y NUMBER
            msiScore = 0.0

            msi1 = self.clause1.verb.msi
            msi2 = self.clause2.verb.msi

            if msi1["person"] == msi2["person"]:
                msiScore = 0.75
                if msi1["number"] == msi2["number"]:
                    msiScore = 1.0
            else:
                msiScore = 0.25
                if msi1["number"] == msi2["number"]:
                    msiScore = 0.5

            equality_box["verb"] = msiScore

            if boxes1["verb"] in self.penality_verbs or boxes2["verb"] in self.penality_verbs:
                equality_box["verb"] = float(equality_box["verb"]) / 2


        #TIME:
        time_score = FactCompare._time_utils.compare_dates(time_data1, time_data2)
        equality_box["time"] = time_score


        #FINAL SCORE:
        available_scores = 0
        sum_scores = 0
        for a_label, a_score in equality_box.iteritems():
            if a_score > -1:
                available_scores += 1
                sum_scores += self.weights[a_label] * a_score


        final_score = 0
        if available_scores > 0:
            final_score = sum_scores/available_scores

        if final_score > 1:
            final_score = 1

        #print fact1
        #print fact2
        #print self.get_boxes(fact1)
        #print self.get_boxes(fact2)
        #print equality_box
        #print final_score
        return final_score
