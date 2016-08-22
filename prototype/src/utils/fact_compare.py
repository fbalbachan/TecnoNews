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

    def __init__(self, clause1, clause2):
        self.clause1 = clause1
        self.clause2 = clause2

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
        if boxes["object"] in [u"alguien", u"algo"]:
            boxes["object"] = u"alguien"

        return boxes

    def compare_entities(self, entity1, entity2, equality_value):
        print entity1
        referent1 = entity1.referent.designated_ref()
        referent2 = entity2.referent.designated_ref()
        msi1 = referent1.msi
        msi2 = referent2.msi
        final_score = 0

        #entity1 != entity2:
        if equality_value == 0.0:

            #ref(entity1) == ref(entity2):
            if str(referent1) == str(referent2):
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



    def compare(self):
        if not self.clause1.is_fact() or not self.clause2.is_fact() or not self.clause1.verb or not self.clause2.verb:
            return 0

        weights = {"subject": 1.2, "verb": 1.1, "object": 0.9, "time": 0.9}

        fact1 = FactNormalizer(self.clause1, FactCompare._ontology).fact()
        fact2 = FactNormalizer(self.clause2, FactCompare._ontology).fact()

        boxes1 = self.get_boxes(fact1)
        boxes2 = self.get_boxes(fact2)

        time_data1 = FactCompare._time_utils.extract_data_info(self.clause1)
        time_data2 = FactCompare._time_utils.extract_data_info(self.clause2)
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
            subject1 = self.clause1.structure("subject").all_entities()[0]
            subject2 = self.clause2.structure("subject").all_entities()[0]
            equality_box["subject"] = self.compare_entities(subject1, subject2, equality_box["subject"])


        #OBJECT:
        object1 = None
        object2 = None
        for a_right_entity in ["od", "regimen", "equative"]:

            if object1 is None and self.clause1.has_structure(a_right_entity):
                object1 = self.clause1.structure(a_right_entity).all_entities()[0]

            if object2 is None and self.clause2.has_structure(a_right_entity):
                object2 = self.clause2.structure(a_right_entity).all_entities()[0]

        if object1 and object2:
            equality_box["object"] = self.compare_entities(object1, object2, equality_box["object"])


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


        #TIME:
        time_score = FactCompare._time_utils.compare_dates(time_data1, time_data2)
        equality_box["time"] = time_score


        #FINAL SCORE:
        available_scores = 0
        sum_scores = 0
        for a_label, a_score in equality_box.iteritems():
            if a_score > -1:
                available_scores += 1
                sum_scores += weights[a_label] * a_score


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
