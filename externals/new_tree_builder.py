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
        self.short_id_dict = {}
        self.fact_compare = FactCompare()

    def get_short_id(self, an_id):
        if an_id not in self.short_id_dict:
            self.short_id_dict[an_id] = len(self.short_id_dict)
        return self.short_id_dict[an_id]

    def build_tree(self, id_noticia, generations=4):
        self.short_id_dict = {}

        #MongoDB Nodes handling:
        ids_to_find = []
        ids_found = []
        node_level = 0;

        #Fact compare auxiliary variables:
        merged_summary_clauses = []
        group_index = 1
        group_threshold = 0.80

        #Result:
        result = {}


        #SET ROOT
        root = self.db["news_entries"].find_one({"wp_id" : int(id_noticia) })
        if root is not None:
            ids_to_find.append(root["_id"])


        while len(ids_to_find) > 0:
            #FILTER ALREADY PROCESSED IDS
            query_id_array = []
            for an_id in ids_to_find:
                if an_id not in ids_found:
                    query_id_array.append(an_id)

            #Fetch nodes
            nodes = self.db["news_entries"].find({"_id" : {"$in": query_id_array} })
            #Empty ids_to_find (because i jost fetched them)
            ids_to_find = []

            for a_node in nodes:
                #Base data for new nodes:
                node_id = self.get_short_id(a_node["_id"])
                node_object = {
                                "edges"     : [],
                                "id"        : a_node["_id"]
                                "title"     : a_node["title"],
                                "date"      : str(a_node["_id"].generation_time).split("+")[0],
                                "url"       : a_node["url"] ,
                                "wp_url"    : a_node["wp_url"] ,
                                "sentiment" : a_node["sentiment"],
                                "geo"       : {
                                    "cities"    : a_node["cities"],
                                    "countries" : a_node["countries"]
                                },
                                "tags"      : a_node["tags"],
                                "categories": a_node["categories"],
                                "source"    : a_node["source"],
                                "summary"   : a_node["summary"],
                                "scored_summary_clauses": [],
                                "level"     : node_level,
                            }

                #Extended summary logic:
                if "extended_summary" in a_node and a_node["extended_summary"] is not None:
                    for clause_index, a_clause in enumerate(a_node["extended_summary"]):
                        node_object["scored_summary_clauses"].append({"text": a_clause["text"], "score": 0, "group": 0})
                        merged_summary_clauses.append({"id": str(node_id) + "-" + str(clause_index), "clause": a_clause, "score_obj": node_object["scored_summary_clauses"][-1]})
                else:
                    node_object["scored_summary_clauses"].append({"text": node_object["summary"], "score": 0, "group": 0})


                # Add child edges if necessary:
                if generations > 0:
                    for a_child_id in a_node["versions"]:
                        node_object["edges"].append(self.get_short_id(a_child_id))

                    #Edges added => i'll need to fetch the additional (destination) nodes:
                    ids_to_find.extend(a_node["versions"])

                #Node data ready: Add to list
                result[node_id] = node_object

            #Decrease generations:
            generations -= 1
            #Increase level:
            node_level += 1
            #Append fetched ids to found ids array
            ids_found.extend(query_id_array)



        #FACT COMPARE:
        for a_clause in merged_summary_clauses:
            for a_clause2 in merged_summary_clauses:
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


        return json.dumps(result, sort_keys=True, indent=4, separators=(',', ': '), cls=JSONEncoder)
        #print merged_summary_clauses



if __name__ == "__main__":
    try :
        root_id = argv[1]
    except :
        print "Debe especificar un id como primer parámetro. Imposible continuar."
        exit(1)

    #print TreeBuilder().build_tree(bson.ObjectId(root_id))
    tree_builder = TreeBuilder()
    print tree_builder.build_tree(root_id)
