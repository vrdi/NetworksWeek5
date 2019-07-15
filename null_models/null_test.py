# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 13:41:51 2019

@author: daryl
"""

import networkx as nx
from gerrychain import Graph
import matplotlib.pyplot as plt
g = Graph.from_json("./County05.json")


n = len(g.nodes())

triangles = []
maxdeg = []
number_leaves=[]
diam = []
number_edges=[]

for i in range(100):
    w = nx.waxman_graph(n,1.25)
    triangles.append(sum(nx.triangles(w).values()))
    maxdeg.append(max(dict(nx.degree(w)).values()))
    number_leaves.append(sum([nx.degree(w)[node] == 1 for node in w.nodes()]))
    if nx.is_connected(w):
        diam.append(nx.diameter(w))
    number_edges.append(len(w.edges()))
    
    

plt.figure()
plt.hist(triangles)
plt.axvline(x =sum(nx.triangles(g).values()),color='r' )
plt.show()


plt.figure()
plt.hist(maxdeg)
plt.axvline(x =max(dict(nx.degree(g)).values()),color='r' )
plt.show()

plt.figure()
plt.hist(number_leaves)
plt.axvline(x =sum([nx.degree(g)[node] == 1 for node in g.nodes()]),color='r' )
plt.show()

plt.figure()
plt.hist(diam)
plt.axvline(x =nx.diameter(g),color='r' )
plt.show()

plt.figure()
plt.hist(number_edges)
plt.axvline(x =len(g.edges()),color='r' )
plt.show()



