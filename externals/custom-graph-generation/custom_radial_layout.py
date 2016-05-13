#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Radial layout for NewsGalaxy plotting with igraph.
    
    @date 20160506 
    @author Daniel Cantarín.
"""

from igraph import *
from bson import ObjectId
import json
import datetime
import math

def polar_to_cartesian( rad, angle ) :
    
    # need to convert angle to radians
    
    radians = angle * math.pi / 180;
    
    # then apply the conversion
    
    ret = ( rad * math.cos( radians ), rad * math.sin( radians ) )
    
    #print "polar_to_cartesian", rad, angle, ret
    
    return ret

def sort_generations( g , criteria="max_size", node_value = 0 ) :
    if not isinstance(g, Graph) :
        raise TypeError('Graph instance expected.')
    
    valid_criterias = ["max_size", "node_index", "node_size", "node_name", "objectid", "wp_id"]
    if criteria not in valid_criterias :
        raise ValueError('Invalid criteria \"' + str(criteria) + "\". Expected values : " + str(valid_criterias))
    
    quantity    =   len(g.vs)
    ret         =   []
    first       =   []
    proc        =   []
    
    if criteria == "max_size" : 
        max_size        =   max(g.vs["size"])
        max_size_items  =   [i for i, v in enumerate(g.vs["size"]) if v == max_size]
        for i in max_size_items :
            first.append( g.vs[i] )
            proc.append( g.vs[i]["name"] )
    elif criteria == "node_index" : 
        first.append( g.vs[node_value] )
        proc.append( g.vs[node_value]["name"] )
    elif criteria == "node_size" : 
        items   =   g.vs.select(size=node_value)
        for v in items :
            first.append( v )
            proc.append( v["name"] )
    elif criteria == "node_name" : 
        v       =   g.vs.find(name=node_value)
        first.append( v )
        proc.append( v["name"] )
    elif criteria == "objectid" : 
        v       =   g.vs.find(objectid=node_value)
        first.append( v )
        proc.append( v["name"] )
    elif criteria == "wp_id" : 
        v       =   g.vs.find(wp_id=node_value)
        first.append( v )
        proc.append( v["name"] )
    
    ret.append(first)
    
    # Once i got the first collection, it's just about looping its edges
    total = 0
    for idx, arr in enumerate(ret) :
        #if idx >= 5 :
        #    break
        
        tmpa = []
        for i, v in enumerate(arr) :
            #print i, v
            total += 1
            try :
                if isinstance(v, Vertex) :
                    item = v
                else : 
                    item = g.vs[v]
                #print idx, total, len(proc) #, len(item.neighbors(1)) # 1 = "OUT"
                
                for c in item.neighbors() :
                    if c["name"] not in proc :
                        proc.append( c["name"] )
                        tmpa.append( c )
            except Exception, e:
                print "ERROR : " + str(e)
                pass
        if tmpa != [] :
            ret.append(tmpa)
    
    # And after the generation sorting process, we re-sort the graph vertices too
    
    nodes   = []
    names   = [] #g.vs["name"][:]
    color   = [] #g.vs["color"][:]
    label   = [] #g.vs["label"][:]
    sizes   = [] #g.vs["size"][:]
    oids    = []
    wpids   = []
    edges   = []
    
    for gn in ret :
        for v in gn :
            nodes.append( v )
            names.append( v["name"] )
            color.append( v["color"] )
            label.append( v["name"].split("_")[1] ) #v["label"] )
            sizes.append( v["size"] )
            oids.append(  v["objectid"] )
            wpids.append( v["wp_id"] )
            
    
    g2 = Graph( len(nodes) - 1 , directed=True )
    g2.vs["name"]       = names
    g2.vs["color"]      = color
    g2.vs["label"]      = label
    g2.vs["size"]       = sizes
    g2.vs["objectid"]   = oids
    g2.vs["wp_id"]      = wpids
    
    for v in g2.vs : 
        for e in g.incident(g.vs.find(name=v["name"]), mode="out") : 
            try :
                g2.add_edge( v, g2.vs.find(name=g.vs[ g.es[e].target ]["name"]) )
            except Exception, ex :
                print g.vs[ g.es[e].target ]["name"] + " not found."
    
    return ret, g2
    

def news_galaxy_radial_layout( g, gens = None) :
    if not isinstance(g, Graph) :
        raise TypeError('Graph instance expected.')
    
    if gens is None :
        raise TypeError('news_galaxy_radial_layout requires a list of generations')
    
    ret         =   []
    generations =   len(gens)
    quantity    =   len(g.vs)
    max_size    =   max(g.vs["size"])
    width       =   (quantity * max_size) + ((max_size + 50) * generations)
    center      =   (width / 2 , width / 2)
    pos         =   center
    
    #for i, v in enumerate(g.vs) : 
    #    if v["size"] > max_size :
    #        max_size = v["size"]
    
    for i, item in enumerate(gens) :
        if not isinstance(item, list) :
            raise TypeError('news_galaxy_radial_layout requires a list of generations. That is, a list of lists. ' + str(type(item)) + " found. Impossible to continue.")
        
        # Each generation has its own layout, depending node quantity
        nodos_locales   =   len(item)
        grados_por_nodo =   0
        radio           =   i * (max_size + 25)
        angulo          =   0
        
        grados_por_nodo = 360 / float(nodos_locales)
        
        angulo = 0
        for i2 in enumerate(item) :
            pos = polar_to_cartesian( radio, angulo )
            ret.append( pos )
            angulo += grados_por_nodo
        
    return ret
    
