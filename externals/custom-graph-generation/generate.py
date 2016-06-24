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
    layout  = "random"
    width   = "1280"
    height  = "1024"

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

    if len(args) >= 3 :
        width = args[2]
        test  = 0
        try:
            test = int(width)
        except Exception, e:
            print "Invalid width \"" + str(width) + "\". Expected positive number."
            exit(1)
        if test <= 0 :
            print "Invalid width \"" + str(width) + "\". Expected positive number."
            exit(1)

    if len(args) >= 4 :
        height = args[3]
        test  = 0
        try:
            test = int(height)
        except Exception, e:
            print "Invalid height \"" + str(height) + "\". Expected positive number."
            exit(1)
        if test <= 0 :
            print "Invalid height \"" + str(height) + "\". Expected positive number."
            exit(1)

    g = None

    if not os.path.exists( args[0] + ".graph.pickle") :
        print datetime.datetime.now()
        print "generating graph from " + args[0] + "..."
        g = gu.create_pickle( args[0], 20 )
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


    if isinstance(layout, list):
        layout = Layout(layout)

    bb = BoundingBox(width, height)
    #layout.fit_into( bbox=(int(width) - 125, int(height) - 200), keep_aspect_ratio=False )
    layout.fit_into( bbox=bb, keep_aspect_ratio=False )
    layout.fit_into( bbox=layout.bounding_box(border=-25), keep_aspect_ratio=True )
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


    tmp = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100%" height="100%" viewBox="0 0 """ + width + " " + height + """ " version="1.1">
<defs>
    <marker id="marker-arrow" markerWidth="8" markerHeight="8" refx="8" refy="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#000" />
    </marker>
    <marker id="marker-red-arrow" markerWidth="8" markerHeight="8" refx="8" refy="3" orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="#F00" />
    </marker>
"""

    #for i,v in enumerate(g.vs) :
    #    for i2, e in enumerate(g.incident(g.vs.find(name=v["name"]), mode="out")):
    #        e2 = g.es[e]
    #        v2 = g.vs[e2.target]
    #        if v["scores"] is not None and len(v["scores"]) > 0 :
    #            st = v["scores"][i2]
    #        else :
    #            st = 40
    #
    #        tmp += """<marker id="marker-text-""" + v["objectid"] + "-" + str(i2) + "\"" + """ markerWidth="10" markerHeight="10" refx="10" refy="3" orient="auto" markerUnits="strokeWidth">"""
    #        tmp += "    <text x=\"0\" y=\"0\">" + str(st) + "</text>"
    #        tmp += "</marker>"

    tmp +="""
</defs>
<g id="graph-nodes">
"""
    if not isinstance(layout, list):
        g.vs["coords"] = coords = layout.coords
    else :
        g.vs["coords"] = coords = layout

    # first the edges, so they later be drawn before the nodes.
    cant = len(g.vs)
    for i,v in enumerate(g.vs) :
        tmp += "    <g class=\"edge-group\" wp_id=\""+v["wp_id"]+"\" label=\""+v["label"]+"\" objectid=\""+v["objectid"]+"\" >\n"
        for i2, e in enumerate(g.incident(g.vs.find(name=v["name"]), mode="out")):
            e2 = g.es[e]
            v2 = g.vs[e2.target]
            if v["scores"] is not None and len(v["scores"]) > 0 :
                if   v["scores"][i2] <= 40 :
                    st = 1
                elif v["scores"][i2] == 50 :
                    st = 4
                elif v["scores"][i2] == 60 :
                    st = 7
                elif v["scores"][i2] == 70 :
                    st = 10
                elif v["scores"][i2] == 80 :
                    st = 12
                elif v["scores"][i2] == 90 :
                    st = 14
                else :
                    st = 16
            else :
                st = 1
            #print "stroke-width", st, v["scores"]

            sw = 1
            if cant <= 50 :
                sw = st

            tmp += "        <line target-id=\""+v2["objectid"]+"\" x1=\""+str(coords[i][0])+"\" y1=\""+str(coords[i][1])+"\" x2=\""+str(v2["coords"][0])+"\" y2=\""+str(v2["coords"][1])+"\" stroke=\"black\" stroke-width=\"" + str(sw) + "\" alt-stroke-width=\"" + str(st) + "\" marker-end=\"url(#marker-arrow)\" marker-mid=\"url(#marker-text-" + v["objectid"] + "-" + str(i2) + ")\" />\n"
        tmp += "    </g>\n"

    # Then, the nodes, that will be drawn on top of the edges.
    nodes_length = len(g.vs)
    for i,v in enumerate(g.vs) :
        tmp += "    <g wp_id=\""+v["wp_id"]+"\" label=\""+v["label"]+"\" objectid=\""+v["objectid"]+"\" stroke=\"black\" fill=\""+v["color"]+"\" stroke-width=\"1\">\n"

        tmp += "        <circle cx=\""+str(coords[i][0])+"\" cy=\""+str(coords[i][1])+"\" r=\""+str(v["size"] / 2 )+"\" />\n"
        tmp += "        <title>"+v["label"]+"</title>\n"
        if len(v["label"]) == 1 :
            cent = 10
        else:
            cent = 0

        text_length = 12
        if (len(v["label"]) >= 3) :
            text_length = 19

        pos_x = (coords[i][0] - v["size"] / 2) + cent
        pos_y = (coords[i][1] + v["size"] / 3) - 2

        if text_length == 12 :
            pos_x = pos_x + 5

        if (len(v["label"]) == 1) :
            pos_x = pos_x - 8

        if (nodes_length <= 50) :
            text_length = 40
            pos_y       = pos_y - 3

        tmp += "        <text x=\""+str( pos_x )+"\" y=\""+str( pos_y )+"\" fill=\"black\" stroke=\"none\" font-family=\"Ubuntu,Tahoma\" font-size=\""+str(int(v["size"]) / 1.8)+"\" textLength=\""+str(text_length)+"\" >"+v["label"]+"</text>"

        tmp += "    </g>\n"

    tmp += "</g>\n"

    tmp += "<g id=\"graph-data\" >\n"
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
