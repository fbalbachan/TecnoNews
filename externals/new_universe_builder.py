#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pymongo import MongoClient
from sys import argv
import bson

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

    def get_short_id(self, an_id):
        if an_id not in self.short_id_dict:
            self.short_id_dict[an_id] = len(self.short_id_dict)
        return self.short_id_dict[an_id]

    def build_tree(self, id_noticia, generations=7):
        self.short_id_dict = {}

        #MongoDB Nodes handling:
        ids_to_find = []
        ids_found = []
        node_level = 0;

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
                                "title"     : a_node["title"],
                                "date"      : str(a_node["_id"].generation_time).split("+")[0],
                                "url"       : a_node["wp_url"] if "wp_url" in a_node and a_node["wp_url"] is not None else a_node["url"],
                                "wp_id"     : a_node["wp_id"] ,
                                "sentiment" : a_node["sentiment"],
                                "categories": a_node["categories"],
                                "source"    : a_node["source"],
                                "level"     : node_level,
                            }

                # Add child edges if necessary:
                if generations > 0:
                    if "universe_versions" in a_node:
                        for idx, a_child_id in enumerate(a_node["universe_versions"]):
                            node_object["edges"].append([self.get_short_id(a_child_id), a_node["universe_scores"][idx]])

                        #Edges added => i'll need to fetch the additional (destination) nodes:
                        ids_to_find.extend(a_node["universe_versions"])

                #Node data ready: Add to list
                result[node_id] = node_object

            #Decrease generations:
            generations -= 1
            #Increase level:
            node_level += 1
            #Append fetched ids to found ids array
            ids_found.extend(query_id_array)

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
