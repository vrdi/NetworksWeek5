# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 13:41:51 2019

@author: daryl
"""

import networkx as nx
from gerrychain import Graph

g = Graph.from_json("./County05.json")


n = len(g.nodes())

triangles = []

for i in range(100):
    w = nx.waxman_graph(n,1)
    triangles.append(sum(nx.triangles(w).values()))
    

plt.figure()
plt.hist(triangles)
plt.axvline(x =sum(nx.triangles(g).values()),color='r' )