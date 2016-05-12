#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Script for custom graphs generation.
    20160512 - Daniel Cantarín.
"""


from igraph import *
from bson import ObjectId
import json
import datetime
import graph_utils as gu
import custom_radial_layout as custom
import os
import sys, getopt


if __name__ == "__main__":
    args    = sys.argv[1:]
    layout  = "customradial"
    
    if len(args) <= 0 :
        print "Sebe ingresar un wp_id. Imposible continuar."
        exit(1)
    
    
    valid_layouts = [
        "customradial", 
        "kawai100", 
        "kawai1000", 
        "kawai2000", 
        "frgrid", 
        "fr", 
        "frcircle", 
        "circle", 
        "drl", 
        "lgl", 
        "random",
        "graphopt",
        "rt",
        "rtcircle",
        "sugiyama",
        "mds",
        "auto"
    ]
    
    if len(args) >= 2 :
        layout =  args[1]
        if layout not in valid_layouts : 
            print "Invalid layout \"" + str(layout) + "\". Expected possible values : " + str(valid_layouts)
            exit(1)
    
    
    g = None
    
    if not os.path.exists( args[0] + ".graph.pickle") :
        print datetime.datetime.now()
        print "generating graph from " + args[0] + "..."
        g = gu.create_pickle( args[0] )
    else :
        print datetime.datetime.now()
        print "loading graph object from file " + args[0] + ".graph.pickle..."
        g = Graph.Load(args[0] + ".graph.pickle", format="pickle")
    
    print datetime.datetime.now()
    print "Loaded. " + str(len(g.vs)) + " vertices, " + str( len(g.es) ) + " edges."

    print datetime.datetime.now()
    print "creating layout..."
    
    if layout == "customradial" :
        gens, g = custom.sort_generations( g )
        #gens, g = custom.sort_generations( g , "node_index", 28)
        #gens, g = custom.sort_generations( g , "node_size", 28)
        #gens, g = custom.sort_generations( g , "node_name", "node_28")
        #gens, g = custom.sort_generations( g , "objectid", args[0] )
        #gens, g = custom.sort_generations( g , "wp_id", "node_28")

        layout = custom.news_galaxy_radial_layout(g, gens )
    elif layout == "kawai100" : 
        layout  = g.layout_kamada_kawai(maxiter=100)
    elif layout == "kawai1000" :
        layout  = g.layout_kamada_kawai(maxiter=1000)
    elif layout == "kawai2000" :
        layout  = g.layout_kamada_kawai(maxiter=2000) 
    elif layout == "frgrid" :
        layout  = g.layout_grid_fruchterman_reingold()
    elif layout == "fr" :
        layout  = g.layout_fruchterman_reingold()
    elif layout == "frcircle" :
        layout  = g.layout_reingold_tilford_circular()
    elif layout == "circle" :
        layout  = g.layout_circle()
    elif layout == "drl" :
        layout  = g.layout_drl()
    elif layout == "lgl" :
        layout  = g.layout_lgl()
    elif layout == "random" :
        layout  = g.layout_random()
    elif layout == "graphopt" :
        layout  = g.layout_graphopt()
    elif layout == "rt" :
        layout  = g.layout_reingold_tilford()
    elif layout == "rtcircle" :
        layout  = g.layout_reingold_tilford_circular()
    elif layout == "sugiyama" :
        layout  = g.layout_sugiyama()
    elif layout == "mds" :
        layout  = g.layout_mds()
    elif layout == "auto" : 
        layout  = g.layout_auto()
    
    
    layout.fit_into( bbox=(1600,1600) )
    print "saving image..."

    print datetime.datetime.now()
    #print "png"
    #plot(g, args[0] + ".png", layout=layout, bbox = (1600, 1600))
    #print datetime.datetime.now()
    #print "svg"
    #plot(g, args[0] + ".svg", layout=layout, bbox = (1600, 1600))
    #print datetime.datetime.now()
    #print "pdf"
    #plot(g, args[0] + ".pdf", layout=layout, bbox = (1600, 1600))
    
    # subgraph / copy by sentiment
    
    
    tmp = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1600pt" height="1600pt" viewBox="0 0 1600 1600" version="1.1">
<g id="graph-nodes">
"""
    g.vs["coords"] = coords = layout.coords
    for i,v in enumerate(g.vs) :
        tmp += "<g wp_id=\""+v["wp_id"]+"\" label=\""+v["label"]+"\" objectid=\""+v["objectid"]+"\" stroke=\"black\" fill=\""+v["color"]+"\" stroke-width=\"1\">\n"
        tmp += "<g class=\"edge-group\">\n"
        for e in g.incident(g.vs.find(name=v["name"]), mode="out") :
            e  = g.es[e]
            v2 = g.vs[e.target]
            tmp += "<line x1=\""+str(coords[i][0])+"\" y1=\""+str(coords[i][1])+"\" x2=\""+str(v2["coords"][0])+"\" y2=\""+str(v2["coords"][1])+"\" stroke=\"gray\" stroke-width=\"1\"/>\n"
        tmp += "</g>\n"
        
        tmp += "<circle cx=\""+str(coords[i][0])+"\" cy=\""+str(coords[i][1])+"\" r=\""+str(v["size"] / 2 )+"\" />\n"
        tmp += "<title>"+v["label"]+"</title>\n"
        
        tmp += "</g>\n"
    
    tmp += "</g>\n"
    
    tmp += "<g class=\"graph-data\" >\n"
    f = open(args[0] + "-set.json","r")
    j = f.read()
    f.close()
    
    import re
    j = re.sub(r"(ObjectId\(')(.{24})('\):)", "'\\2':", j)
    
    tmp += json.dumps(eval(j), sort_keys=True, indent=4, separators=(',', ': '), cls=gu.JSONEncoder) 
    tmp += "</g>\n"
    tmp += "</svg>"
    f = open(args[0] + ".svg","w")
    f.write(tmp)
    f.close()
    
    print datetime.datetime.now()
    print "done."
    
