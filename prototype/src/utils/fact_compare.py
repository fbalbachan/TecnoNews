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
        halfs = a_fact.split("--TIME:")
        time = halfs[1].strip().lower()
        if time == "":
            time = None

        parts = halfs[0].split("+")
        if len(parts) < 2:
            return None

        boxes = {"subject": parts[0].strip(), "verb": parts[1].strip(), "object": None, "time": time}
        if len(parts) == 3:
            boxes["object"] = parts[2].strip()

        if boxes["subject"] in [u"alguien", u"algo"]:
            boxes["subject"] = u"alguien"
        if boxes["object"] in [u"alguien", u"algo"]:
            boxes["object"] = u"alguien"

        return boxes


    def compare(self):
        if not self.clause1.is_fact() or not self.clause2.is_fact():
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

        #REFERENT:
        if equality_box["subject"] == 0.0:
            subject_ref1 = self.clause1.structure("subject").all_entities()[0].referent.designated_ref()
            subject_ref2 = self.clause2.structure("subject").all_entities()[0].referent.designated_ref()
            if str(subject_ref1) == str(subject_ref2):
                equality_box["subject"] = 1.0
            else:
                msi1 = subject_ref1.msi
                msi2 = subject_ref2.msi
                msiScore = 0.0
                if msi1["person"] == msi2["person"] and msi1["number"] == msi2["number"] and msi1["animity"] == msi2["animity"]:
                    msiScore = 0.7
                else:
                    if msi1["person"] == msi2["person"]:
                        msiScore = 0.20
                        if msi1["animity"] == msi2["animity"]:
                            msiScore = 0.35
                    elif msi1["number"] == msi2["number"]:
                        msiScore = 0.15
                        if msi1["animity"] == msi2["animity"]:
                            msiScore = 0.25



        #VERB:
        if equality_box["verb"] == 1.0:
            #TIME y PERSON y NUMBER
            msi1 = self.clause1.verb.msi
            msi2 = self.clause2.verb.msi
            msiScore = 0.0

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
