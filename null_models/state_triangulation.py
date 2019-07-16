import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import numpy as np
import networkx as nx
import math
from sklearn.neighbors import KDTree
import geopandas as gpd
import numpy as np
import networkx as nx
import math
import geopandas as gpd
import pysal as ps
from sklearn.neighbors import KDTree
from gerrychain import Graph
import csv
import os
from functools import partial
import json
import numpy as np
import geopandas as gpd
import seaborn as sns


df = gpd.read_file("./County05.shp")
rW = ps.rook_from_shapefile("./County05.shp")

#df["geometry"] = df.geometry.buffer(1)
#ps.weights.Rook.from_dataframe(df)
g2 = nx.Graph(rW.neighbors)
centroids = df.centroid
c_x = centroids.x
c_y = centroids.y
ctds={x:(c_x[int(x)],c_y[int(x)]) for x in rW.neighbors.keys()}

num_points = len(centroids)

tri = Delaunay([(c_x[n],c_y[n]) for n in range(num_points)])

nlist = tri.vertex_neighbor_vertices

g = nx.Graph()

for n in range(num_points):
    g.add_edges_from([(n,x) for x in nlist[1][nlist[0][n]:nlist[0][n+1]]])
    
pos = { n : (c_x[n],c_y[n]) for n in range(num_points)}

plt.figure()
nx.draw(g,pos=pos,node_size=.1,width=.4,node_color='k')
plt.show()




"""
g3 = nx.Graph()

for edge in g.edges():
    if     math.sqrt((pos[edge[0]][0]-pos[edge[1]][0])**2+(pos[edge[0]][1]-pos[edge[1]][1])**2) <radius:
        g3.add_edge(edge[0],edge[1])


plt.figure()
nx.draw(g3,pos=pos,node_size=.1,width=.4,node_color='k')
plt.show()
"""

lens=[]
for edge in g.edges():
    lens.append(math.sqrt((pos[edge[0]][0]-pos[edge[1]][0])**2+(pos[edge[0]][1]-pos[edge[1]][1])**2))

plt.figure()
plt.hist(lens)
plt.show()

radius = 3*min(lens)

h = nx.Graph()


for n1 in g.nodes():
    h.add_node(n1)
    for n2 in g.nodes():
        if n1!=n2:
            if math.sqrt((pos[n1][0]-pos[n2][0])**2+(pos[n1][1]-pos[n2][1])**2) < radius:
                h.add_edge(n1,n2)
                
                
plt.figure()
nx.draw(h,pos=pos,node_size=.1,width=.4,node_color='k')
plt.show() 

h = nx.Graph()


X = np.array([(c_x[n],c_y[n]) for n in range(num_points)])
kdt = KDTree(X, leaf_size=30, metric='euclidean')
nbrs = kdt.query(X, k=10, return_distance=False)  

h = nx.Graph()

for n in range(num_points):
    for l in nbrs[n]:
        if l!=n:
            h.add_edge(n,l)


plt.figure()
nx.draw(h,pos=pos,node_size=.1,width=.4,node_color='k')
plt.show()


"""
h2 = nx.Graph()

for n in range(num_points):
    for l in nbrs[n]:
        if l!=n:
            if (n,l) in h.edges() or (l,n) in h.edges(): #tried g
                h2.add_edge(n,l)


plt.figure()
nx.draw(h2,pos=pos,node_size=.1,width=.4,node_color='k')
plt.show()
"""