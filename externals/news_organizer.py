#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pymongo import MongoClient
from sys import argv
import bson
from datetime import datetime, timedelta

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
        #print db.command("serverStatus")
        #exit()

        self.db     = db
        self.client = client

class NewsOrganizer(BaseInfo) :
    def __init__(self):
        super(NewsOrganizer, self).__init__()
        self.short_id_dict = {}

    def get_short_id(self, an_id):
        if an_id not in self.short_id_dict:
            self.short_id_dict[an_id] = len(self.short_id_dict)
        return self.short_id_dict[an_id]

    def organize(self, language, days, categories):
        self.short_id_dict = {}


        fromDate = datetime.utcnow() - timedelta(days=days)
        fromIdDate = bson.ObjectId.from_datetime(fromDate)
        items = self.db["news_entries"].find({"_id" : {"$gt" : fromIdDate }, "language":language}, {"_id":1, "versions":1, "categories":1, "title": 1, "wp_url": 1, "url": 1})
        
        withChildren = set()
        withParents  = set()

        newsDict = {}
        referenceDict = {}
        
        # Fill dictionary with full news
        for mongoObject in items:
            if mongoObject["versions"] is None:
                mongoObject["versions"] = []
            newsObject = {
                            "generation_time": mongoObject["_id"].generation_time.isoformat().replace("T", " ")[:-6],
                            "total_children": len(mongoObject["versions"]),
                            "total_parents": 0,
                            "title": mongoObject["title"],
                            "categories": mongoObject["categories"],
                            "url": mongoObject["url"],
                            "wp_url": mongoObject["wp_url"]
                         }
            shortId = self.get_short_id(mongoObject["_id"])
            newsDict[shortId] = newsObject
            
            # Can also complete this set:
            if newsObject["total_children"] > 0:
                withChildren.add(shortId)
            
            # Fill reference dictionary: some reference may come before the referenced object!
            for aReference in mongoObject["versions"]:
                if self.get_short_id(aReference) not in referenceDict:
                    referenceDict[self.get_short_id(aReference)] = 0
                referenceDict[self.get_short_id(aReference)] += 1
                
        # Once references had been counted save them into news object    
        for aShortId in referenceDict:
            if aShortId in newsDict:
                newsDict[aShortId]["total_parents"] = referenceDict[aShortId]

                # Can also complete this set:
                if newsDict[aShortId]["total_parents"] > 0:
                    withParents.add(aShortId)

        # Filter by category
        filteredNews = []
        for aNewsId in newsDict.keys():
            if "all" in categories or any(aCat in categories for aCat in newsDict[aNewsId]["categories"]):
                filteredNews.append(aNewsId)

        allNews = set(filteredNews)
        withParents = withParents & allNews
        withChildren = withChildren & allNews

        newsDict = {k:v for k,v in newsDict.iteritems() if k in allNews} 
        # END FILTER

        returnObj = {}
	returnObj["stats"] = [
                              "TOTAL: " + str(len(allNews)), 
                              "With Children and Parents (VIP News - Very ImPortant news): " + str(len(withChildren & withParents)), 
                              "With Children only (Discontinued news): " + str(len(withChildren - withParents)), 
                              "With Parents only (Breaking news at that moment): " + str(len(withParents - withChildren)), 
                              "With no children nor parents (Trivial news or fake news candidates): " + str(len(allNews - withChildren - withParents))
                             ]
        returnObj["entries"] = []
        #print "TOTAL: " + str(len(allNews))
        #print "With Children and Parents (VIP News - Very ImPortant news): " + str(len(withChildren & withParents))
        #print "With Children only (Discontinued news): " + str(len(withChildren - withParents))
        #print "With Parents only (Breaking news at that moment): " + str(len(withParents - withChildren))
        #print "With no children nor parents (Trivial news or fake news candidates): " + str(len(allNews - withChildren - withParents))
        
        for anId in allNews:
            if anId in (withChildren & withParents):
                newsDict[anId]["type"] = "VIP"
            elif anId in (withChildren - withParents):
                newsDict[anId]["type"] = "Discontinued"
            elif anId in (withParents - withChildren):
                newsDict[anId]["type"] = "Breakingnews"
            else:
                newsDict[anId]["type"] = "Trivial"
            
            #print newsDict[anId]["type"] + '|' + newsDict[anId]["title"].encode('utf-8') + '|' + str(newsDict[anId]["categories"]) + '|' + str(newsDict[anId]["generation_time"])
            
        def compareFunction(item1, item2):
            typeMap = {"Breakingnews": 0, "VIP": 1, "Discontinued" : 2, "Trivial": 3}
            if str(item1["categories"]) > str(item2["categories"]):
                return 1
            elif str(item1["categories"]) < str(item2["categories"]):
                return -1
            else:
                if typeMap[item1["type"]] > typeMap[item2["type"]]:
                    return 1
                elif typeMap[item1["type"]] < typeMap[item2["type"]]:
                    return -1
                else:
                    if item1["title"] > item2["title"]:
                        return 1
                    elif item1["title"] < item2["title"]:
                        return -1
                    else:
                        return 0
                        
        for anItem in sorted(newsDict.values(), cmp=compareFunction):
            #print anItem["type"] + '|' + anItem["title"].encode('utf-8') + '|' + str(anItem["categories"]) + '|' + str(anItem["generation_time"])
            returnObj["entries"].append(anItem)


        return json.dumps(returnObj, sort_keys=True, indent=4, separators=(',', ': '), cls=JSONEncoder)
        #print merged_summary_clauses



if __name__ == "__main__":
    try :
        language = argv[2]
        days = int(argv[1])
        categories_len = int(argv[3])
	categories = []
        for i in range(4, 4+categories_len):
            categories.append(argv[i].replace("_", " ").decode("utf-8"))
    except :
        print "ERROR"
        exit(1)

    organizer = NewsOrganizer()
    print organizer.organize(language, days, categories)
