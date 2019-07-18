# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 11:02:47 2019

@author: daryl
"""

from FKT import *
import networkx as nx #Requires at least networkx 2.3+
import matplotlib.pyplot as plt
import random
import math
import numpy as np
import time
import seaborn as sns


def get_spanning_tree_u_w(G):
    node_set=set(G.nodes())
    x0=random.choice(tuple(node_set))
    x1=x0
    while x1==x0:
        x1=random.choice(tuple(node_set))
    node_set.remove(x1)
    tnodes ={x1}
    tedges=[]
    current=x0
    current_path=[x0]
    current_edges=[]
    while node_set != set():
        next=random.choice(list(G.neighbors(current)))
        current_edges.append((current,next))
        current = next
        current_path.append(next)

        if next in tnodes:
            for x in current_path[:-1]:
                node_set.remove(x)
                tnodes.add(x)
            for ed in current_edges:
                tedges.append(ed)
            current_edges = []
            if node_set != set():
                current=random.choice(tuple(node_set))
            current_path=[current]


        if next in current_path[:-1]:
            current_path.pop()
            current_edges.pop()
            for i in range(len(current_path)):
                if current_edges !=[]:
                    current_edges.pop()
                if current_path.pop() == next:
                    break
            if len(current_path)>0:
                current=current_path[-1]
            else:
                current=random.choice(tuple(node_set))
                current_path=[current]


    return tedges


def get_spanning_tree_u_ab(G):
    node_set=set(G.nodes())
    x0=random.choice(tuple(node_set))

    node_set.remove(x0)

    current=x0
    tedges=[]

    while node_set != set():
        next=random.choice(list(G.neighbors(current)))
        if next in node_set:
            node_set.remove(next)
            tedges.append((current, next))
        current=next


    return tedges


def tree_cycle_walk_cut(T,G):

    tempo=0
    tedges=set(T.edges())
    newT = T.copy()
    while tempo==0:
        #edge = (random.choice(tuple(T.nodes())),random.choice(tuple(T.nodes())))
        edge = random.choice(list(G.edges()))
        if (edge[0],edge[1]) not in tedges and (edge[1],edge[0]) not in tedges:
            tempo=1
            newT.add_edge(edge[0],edge[1])
            ncycle=nx.find_cycle(newT,edge[0])
            cutedge=random.choice(tuple(ncycle))
            newT.remove_edge(cutedge[0],cutedge[1])
    return newT



diams = []
radii = []
avgpath = []

for i in range(1000):

    #t= get_spanning_tree_u_w(nx.grid_graph([4,5]))
    t= get_spanning_tree_u_w(nx.complete_graph(20))
    tgraph=nx.Graph()
    tgraph.add_edges_from(t)
    
    diams.append(nx.diameter(tgraph))
    radii.append(nx.radius(tgraph))
    avgpath.append(nx.average_shortest_path_length(tgraph))
    

diams2 = []
radii2 = []
avgpath2 = []
accept = []

G= nx.grid_graph([4,5])
G = nx.complete_graph(20)
t= get_spanning_tree_u_w(G)
tgraph=nx.Graph()
tgraph.add_edges_from(t)
tgraphs = [tgraph]

pos = nx.kamada_kawai_layout(tgraph)#spectral_layout(G)#
for i in range(1000):
    #plt.figure()
    #nx.draw(tgraphs[-1],pos = pos)
    #plt.show()
    tempT = tree_cycle_walk_cut(tgraphs[-1],G)
    
    if nx.radius(tgraphs[-1]) > nx.radius(tempT):
        
        tgraphs.append(tempT)
        accept.append(1)
    else:
        if random.random() < .001:
            tgraphs.append(tempT)
            accept.append(2)
        else:
            accept.append(0)
            
            
    diams2.append(nx.diameter(tgraphs[-1]))
    radii2.append(nx.radius(tgraphs[-1]))
    avgpath2.append(nx.average_shortest_path_length(tgraphs[-1]))
            
            
            
    #tgraphs
    


# 
#
#
    
#plt.figure()
#nx.draw(tgraph,pos = {x:x for x in tgraph.nodes()})
#plt.show()

