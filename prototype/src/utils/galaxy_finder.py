#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pymongo
from src.services.mongodb.connector import MongoConnector
from bson.objectid import ObjectId
from sys import argv
import bson


class TreeBuilder(object):
    def __init__(self, mode=None):
        self.short_id_dict = {}
        self.db = MongoConnector.get_instance(mode)

    def get_short_id(self, an_id):
        if an_id not in self.short_id_dict:
            self.short_id_dict[an_id] = len(self.short_id_dict)
        return self.short_id_dict[an_id]

    def build_many(self):
        categories = ["economía", "política", "tecnología", "ciencia", "deporte", "interés general", "internacionales", "policiales", "clima", "estilo vida", "turismo", "propiedades", "mujer", "entretenimiento", "automóviles", "salud", "electrodomésticos"]
        categories = ["interés general"]
        output = ""
        for a_category in categories:
            galaxies = self.db["news_entries"].find({"categories": a_category, "versions.0": {"$exists": True}}).sort("_id", pymongo.DESCENDING)
            max_sample = 5
            max_sample = 50
            for a_galaxy in galaxies:
                if max_sample == 0:
                    break
                max_sample -= 1
                output += "\n--------------------------"
                output += "\n--------------------------"
                output += self.build_tree(str(a_galaxy["_id"]))
        return output

    def build_tree(self, id_noticia, generations=1):
        self.short_id_dict = {}

        # MongoDB Nodes handling:
        ids_to_find = []
        ids_found = []
        node_level = 0

        # Result:
        result = {}

        # SET ROOT
        root = self.db["news_entries"].find_one({"_id": ObjectId(id_noticia)})
        if root is not None:
            ids_to_find.append(root["_id"])

        while len(ids_to_find) > 0:
            # FILTER ALREADY PROCESSED IDS
            query_id_array = []
            for an_id in ids_to_find:
                if an_id not in ids_found:
                    query_id_array.append(an_id)

            # Fetch nodes
            nodes = self.db["news_entries"].find({"_id": {"$in": query_id_array}})
            # Empty ids_to_find (because i jost fetched them)
            ids_to_find = []

            for a_node in nodes:
                # Base data for new nodes:
                node_id = self.get_short_id(a_node["_id"])
                node_object = {"edges":        [],
                               "title":        a_node["title"],
                               "date":         str(a_node["published_date"]).split("+")[0],
                               "categories":   a_node["categories"],
                               "level":        node_level,
                               'scores':       [],
                               'source':       a_node['source']
                               }

                # Add child edges if necessary:
                if generations > 0:
                    for idx, a_child_id in enumerate(a_node["versions"]):
                        node_object["edges"].append(self.get_short_id(a_child_id))
                        node_object["scores"].append(a_node['universe_scores'][idx])

                    # Edges added => i'll need to fetch the additional (destination) nodes:
                    ids_to_find.extend(a_node["versions"])

                # Node data ready: Add to list
                result[node_id] = node_object

            # Decrease generations:
            generations -= 1
            # Increase level:
            node_level += 1
            # Append fetched ids to found ids array
            ids_found.extend(query_id_array)

        root = result[0]
        output = ""
        output += ("\nNoticia: \"%s\"   (%s   -   %s)" % (root['title'], root['date'], root['source']))

        for idx, a_child in enumerate(root["edges"]):
            child = result[a_child]
            output += ("\n     Misma noticia: \"%s\"      (%s   -   %s)   | Probabilidad porcentual: %d" % (child['title'], child['date'], child['source'], int(root["scores"][idx])))
        # print json.dumps(result, sort_keys=True, indent=4, separators=(',', ': '), cls=JSONEncoder)

        # print merged_summary_clauses
        return output


if __name__ == "__main__":
    try:
        root_id = argv[1]
    except Exception as e:
        print("Debe especificar un id como primer parámetro. Imposible continuar.")
        exit(1)

    # print TreeBuilder().build_tree(bson.ObjectId(root_id))
    tree_builder = TreeBuilder()
    print(tree_builder.build_many())
