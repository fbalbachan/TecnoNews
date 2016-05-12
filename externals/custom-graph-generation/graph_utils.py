#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Util function for file handling, mongodb querying, etc.
    
    @author Daniel Cantarin
    @date 20160510
'''

from igraph import *
from bson import ObjectId
import json
import datetime

class JSONEncoder(json.JSONEncoder):
    
    def parse_dict(self, d) :
        ret = {}
        for k in d :
            k2 = str(k)
            if isinstance(d[k], dict) :
                ret[k2] = self.parse_dict(d[k])
            else :
                ret[k2] = d[k]
        return ret
    
    def default(self, o):
        #print "default", o
        #if isinstance(o, dict):
        #    print o
        #    return self.parse_dict(o)
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def color_from_sentiment(sent = None) :
    ret = "white"
    
    if sent != None :
        if "negative" in sent.lower() :
            ret = "red"
        if "positive" in sent.lower() :
            ret = "green"

    return ret

def generate_json_from_objectid( item_id , gens = 5) :
    from bson.objectid import ObjectId
    import json
    from pymongo import MongoClient

    import os.path
    already_processed = {}

    mongo_data = {
        "host"  :   "85.10.210.172",
        "port"  :   27017,
        "db"    :   "sentinews_entrebit",
        "username" : "root",
        "password" : "NaturalezaMuerta"
    }

    client = MongoClient(mongo_data["host"], mongo_data["port"])

    if "username" in mongo_data :
        client["admin"].authenticate( mongo_data["username"], mongo_data["password"])

    db  =   client[mongo_data["db"]]
    col =   db["news_entries"]

    result = col.find({"wp_id" : { "$in" : [ item_id , str(item_id) ]} })[0]

    to_check = []
    to_check.extend(result["versions"])

    current_id = 0

    already_processed[(result["_id"])] = {"id": "node_" + str(current_id), "date" : "", "wp_id": str(result["wp_id"]), "oid": str(result["_id"]), "title": result["title"], "source": result["source"], "cats": result["categories"], "children": result["versions"]}
    if "sentiment" in result :
        already_processed[(result["_id"])]["sentiment"] = result["sentiment"]


    looped = 0
    while to_check:
        result = col.find({"_id":{"$in":to_check}})

        next_level_ids = set()
        for checked in result:
            current_id += 1
            try :
                already_processed[checked["_id"]] = {"id": "node_" + str(current_id), "date" : "", "wp_id": str(checked["wp_id"]), "oid": str(checked["_id"]), "cats": checked["categories"], "source": checked["source"],  "title": checked["title"], "children": checked["versions"]}
                if "sentiment" in checked :
                    already_processed[checked["_id"]]["sentiment"] = checked["sentiment"]
            except Exception, e :
                print e
                print checked
                exit(1)
            next_level_ids.update(checked["versions"])


        to_check=list(next_level_ids)
        to_check = [an_id for an_id in to_check if an_id not in already_processed]

        looped += 1
        if looped >= gens:
            break

    #print( "total ids : " + str(current_id) )
    
    final_graph = {}
    for an_id, a_value in already_processed.iteritems():

        for a_child in a_value["children"]:

            if a_child not in already_processed:
                continue
            
            child_id    = already_processed[a_child]["id"]
            child_title = already_processed[a_child]["title"]
            child_oid   = already_processed[a_child]["oid"]
            child_wpid  = already_processed[a_child]["wp_id"]
            child_cats  = already_processed[a_child]["cats"]
            child_source= already_processed[a_child]["source"]
            child_date  = already_processed[a_child]["date"]
            if "sentiment" in already_processed[a_child] :
                child_sentiment = already_processed[a_child]["sentiment"]
            else :
                child_sentiment = None

            if child_id not in final_graph:
                final_graph[child_id] = {"sentiment" : child_sentiment, "date" : child_date, "oid" : child_oid, "wp_id" : child_wpid , "cats" : child_cats, "source" : child_source, "title" : child_title, "referents": [], "children" : []}
            
            if a_value["id"] not in final_graph:
                final_graph[a_value["id"]] = {"sentiment" : a_value["sentiment"], "cats" : a_value["cats"], "source" : a_value["source"], "oid" : a_value["oid"], "wp_id" : a_value["wp_id"] ,"title" : a_value["title"], "referents": [], "children" : []}

            final_graph[a_value["id"]]["children"].append(child_id)
            final_graph[child_id]["referents"].append(a_value["id"])
        
        

    #print already_processed
    f = open(item_id + "-set.json", "w")
    #f.write( json.dumps(already_processed, sort_keys=True, indent=4, separators=(',', ': '), cls=JSONEncoder) )
    f.write( repr(already_processed) )
    f.close()
    f = open(item_id + "-final.json", "w")
    #f.write( json.dumps(already_processed, sort_keys=True, indent=4, separators=(',', ': '), cls=JSONEncoder) )
    f.write( repr(final_graph) )
    f.close()
    
    return final_graph

def create_pickle( object_id ) :
    # Read a common input.
    
    if not os.path.exists( object_id + "-set.json") or not os.path.exists( object_id + "-final.json") :
        generate_json_from_objectid( object_id )
    
    print datetime.datetime.now()
    print "reading input data..."
    f = open(object_id + "-set.json","r")
    j = f.read()
    f.close()
    already_processed = eval(j)
    f = open(object_id + "-final.json","r")
    j = f.read()
    f.close()
    semi_final_graph = eval(j)
    final_graph = []
    names = []
    color = []
    label = []
    sizes = []
    oids  = []
    wpids = []
    
    i = 0
    for item in semi_final_graph :
        final_graph.append( semi_final_graph[item] )
        #final_graph[len(final_graph) - 1]["name"] = item
        names.append(item)
        color.append( color_from_sentiment( semi_final_graph[item]["sentiment"] ) )
        #label.append( semi_final_graph[item]["title"][:22].encode("utf-8") + "..." )
        label.append( str(i) )
        sizes.append( 5 + len(semi_final_graph[item]["referents"]) + len(semi_final_graph[item]["children"]) )
        oids.append( semi_final_graph[item]["oid"] )
        wpids.append( semi_final_graph[item]["wp_id"] )
        i += 1


    print datetime.datetime.now()
    print "creating graph object..."
    g       =   Graph( directed=True )
    l       =   []
    i       =   0
    g.add_vertices(len(final_graph))
    g.delete_edges(g.es)
    g.vs["name"]        = names
    g.vs["color"]       = color
    g.vs["label"]       = label
    g.vs["size"]        = sizes
    g.vs["objectid"]    = oids
    g.vs["wp_id"]       = wpids

    '''
    for v in g.vs :
        l.append( str(i) )
        i = i + 1
    '''

    
    print datetime.datetime.now()
    print "looping edges..."
    e  = 0
    for i in range(0, len(final_graph)) :
        item = final_graph[i]
        # print item
        for ref in item["referents"]:
            g.add_edge( ref, i )
            e += 1
            '''
            e2 = 0
            for item2 in final_graph :
                e2 += 1
                if item2["id"] == ref :
                    g.add_edge(e2, i)
                    e += 1
                    break
            '''
    g.save(object_id + ".graph.pickle", format="pickle")
    
    return g
    
