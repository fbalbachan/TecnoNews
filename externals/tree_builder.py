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
    
    def build_tree(self, id_noticia):
        
        #web.header('Content-Type', 'application/json')
        #root = self.db["news_entries"].find({"_id" : bson.ObjectId(id_noticia) })
        root = self.db["news_entries"].find({"wp_id" : int(id_noticia) })

        ret = { "root" : id_noticia }
        
        if root.count() > 0 :
            root = root[0]
            tmp  = self._get_simplified(root)
            
            tmp["children"] = self._get_children( root )
            
            for item in tmp["children"] : 
                item["children"] = self._get_children(item)
                for item2 in item["children"] :
                    item2["children"] = self._get_children(item2)
                    for item3 in item2["children"] :
                        item3["children"] = self._get_children(item3)
                        #for item4 in item3["children"] :
                        #    item4["children"] = self._get_children(item4)
                        #    #for item5 in item4["children"] :
                        #    #    item5["children"] = self._get_children(item5)
                        #    #    for item6 in item5["children"] :
                        #    #        item6["children"] = self._get_children(item6)
                        #    #        for item7 in item6["children"] :
                        #    #            item7["children"] = self._get_children(item7)
            
            ret["root"] = tmp
        
        return json.dumps(ret, sort_keys=True, indent=4, separators=(',', ': '), cls=JSONEncoder)
    
    def _get_children(self, obj) :
        
        children = []
        ret      = []
        
        if "versions" in obj:
            children = self.db["news_entries"].find({"_id" : {"$in" : obj["versions"]} })
        
        for c in children :
            ret.append( self._get_simplified( c ) )
        
        return ret
        
    def _get_simplified(self, obj) :
        tmp  = {
            "id"        : str(obj["_id"]), 
            "title"     : obj["title"], 
            "url"       : obj["url"] ,
            "wp_url"    : obj["wp_url"] , 
            "date"      : str(obj["published_date"]),
            "sentiment" : obj["sentiment"],
            "geo"       : {
                "cities"    : obj["cities"],
                "countries" : obj["countries"]
            },
            "tags"      : obj["tags"],
            "categories": obj["categories"],
            #"entities"  : obj["entities"],
            "summary"   : obj["content"].replace(".\n",". ").replace("\n", ". ").split(". ")[0] + ".",
            "source"    : obj["source"]
        }
        
        if "versions" in obj and obj["versions"] is not None:
            tmp["versions"] = obj["versions"]

        return tmp
        


if __name__ == "__main__":
    try :
        root_id = argv[1]
    except :
        print "Debe especificar un id como primer parámetro. Imposible continuar."
        exit(1)
    
    #print TreeBuilder().build_tree(bson.ObjectId(root_id))
    print TreeBuilder().build_tree(root_id)

