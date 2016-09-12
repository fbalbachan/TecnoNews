#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pymongo import MongoClient
from sys import argv
import bson
from src.utils.fact_compare import FactCompare

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bson.ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


mongo_data = {
    "host"  :   "85.10.210.172",
    "port"  :   27017,
    "db"    :   "sentinews_entrebit",
    "username" : "root",
    "password" : "NaturalezaMuerta"
}


class BaseInfo(object):
    def __init__(self):
        client = MongoClient(mongo_data["host"], mongo_data["port"])

        if "username" in mongo_data :
            client["admin"].authenticate( mongo_data["username"], mongo_data["password"])

        db = client[mongo_data["db"]]

        self.db     = db
        self.client = client


class TreeBuilder(BaseInfo) :
    def __init__(self):
        super(TreeBuilder, self).__init__()
        self.summary_clauses = []
        self.fact_compare = FactCompare()

    def build_tree(self, id_noticia):
        self.summary_clauses = []
        #web.header('Content-Type', 'application/json')
        #root = self.db["news_entries"].find({"_id" : bson.ObjectId(id_noticia) })
        root = self.db["news_entries"].find({"wp_id" : int(id_noticia) })

        ret = { "root" : id_noticia }

        if root.count() > 0 :
            root = root[0]
            tmp  = self._get_simplified(root)

            tmp["children"] = self._get_children( root, root["categories"] )

            for item in tmp["children"] :
                item["children"] = self._get_children(item, root["categories"])
                for item2 in item["children"] :
                    item2["children"] = self._get_children(item2, root["categories"])
                    for item3 in item2["children"] :
                        item3["children"] = self._get_children(item3, root["categories"])
                        #for item4 in item3["children"] :
                        #    item4["children"] = self._get_children(item4)
                        #    #for item5 in item4["children"] :
                        #    #    item5["children"] = self._get_children(item5)
                        #    #    for item6 in item5["children"] :
                        #    #        item6["children"] = self._get_children(item6)
                        #    #        for item7 in item6["children"] :
                        #    #            item7["children"] = self._get_children(item7)

            ret["root"] = tmp

        group_index = 1
        group_threshold = 0.85
        for a_clause in self.summary_clauses:
            for a_clause2 in self.summary_clauses:
                if a_clause["id"] == a_clause2["id"]:
                    continue
                comparison_score = self.fact_compare.test_compare(a_clause["clause"], a_clause2["clause"])
                comparison_score = round(comparison_score, 2)

                if comparison_score >= group_threshold:
                    if a_clause["score_obj"]["group"] == 0 and a_clause2["score_obj"]["group"] == 0:
                        a_clause["score_obj"]["group"] = group_index
                        a_clause2["score_obj"]["group"] = group_index
                        group_index += 1
                    elif a_clause["score_obj"]["group"] != 0 and a_clause2["score_obj"]["group"] == 0:
                        a_clause2["score_obj"]["group"] = a_clause["score_obj"]["group"]
                    elif a_clause["score_obj"]["group"] == 0 and a_clause2["score_obj"]["group"] != 0:
                        a_clause["score_obj"]["group"] = a_clause2["score_obj"]["group"]

                if comparison_score > a_clause["score_obj"]["score"]:
                    a_clause["score_obj"]["score"] = comparison_score

        return json.dumps(ret, sort_keys=True, indent=4, separators=(',', ': '), cls=JSONEncoder)

    def _get_children(self, obj, root_categories) :

        children = []
        ret      = []

        if "versions" in obj:
            children = self.db["news_entries"].find({"_id" : {"$in" : obj["versions"]}, "categories" : {"$in" : root_categories} })
            if children is None:
                children = []

        for c in children :
            ret.append( self._get_simplified( c ) )

        return ret

    def _get_simplified(self, obj) :
        tmp  = {
            "id"        : str(obj["_id"]),
            "title"     : obj["title"],
            "url"       : obj["url"] ,
            "wp_url"    : obj["wp_url"] ,
            "date"      : str(obj["_id"].generation_time).split("+")[0], #str(obj["published_date"])
            "sentiment" : obj["sentiment"],
            "geo"       : {
                "cities"    : obj["cities"],
                "countries" : obj["countries"]
            },
            "tags"      : obj["tags"],
            "categories": obj["categories"],
            #"entities"  : obj["entities"],
            "summary"   : obj["content"].replace(".\n",". ").replace("\n", ". ").split(". ")[0] + ".",
            "scored_summary_clauses": [],
            "source"    : obj["source"],
        }

        if "summary" in obj and obj["summary"] is not None:
            tmp["summary"] = obj["summary"].replace("\n", ". ")

        if "versions" in obj and obj["versions"] is not None:
            tmp["versions"] = obj["versions"]


        if "extended_summary" in obj and obj["extended_summary"] is not None:
            for a_clause in obj["extended_summary"]:
                tmp["scored_summary_clauses"].append({"text": a_clause["text"], "score": 0, "group": 0})
                self.summary_clauses.append({"id": tmp["id"], "clause": a_clause, "score_obj": tmp["scored_summary_clauses"][-1]})
        else:
            tmp["scored_summary_clauses"].append({"text": tmp["summary"], "score": 0, "group": 0})

        return tmp



if __name__ == "__main__":
    try :
        root_id = argv[1]
    except :
        print "Debe especificar un id como primer parámetro. Imposible continuar."
        exit(1)

    #print TreeBuilder().build_tree(bson.ObjectId(root_id))
    tree_builder = TreeBuilder()
    print tree_builder.build_tree(root_id)
    #print json.dumps(tree_builder.summary_clauses, sort_keys=True, indent=4, separators=(',', ': '), cls=JSONEncoder)
