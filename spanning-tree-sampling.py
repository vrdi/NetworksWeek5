#!/usr/bin/env python
# coding: utf-8

# In[108]:


#from FKT import *
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

def try_balanced_cut(T, num_tries):
    i = 0
    while i < num_tries:
        T = T
        edge_set = set(T.edges())
        #print(edge_set)
        snip_edge = random.choice(tuple(edge_set))
        T.remove_edge(snip_edge[0], snip_edge[1])
        components = list(nx.connected_components(T))
        if len(components) == 1:
            T.add_edge(snip_edge[0], snip_edge[1])
            i += 1
        if len(components) == 2:
            if abs(len(components[0]) - len(components[1])) < 2:
                i = num_tries
                return True
            else:
                T.add_edge(snip_edge[0], snip_edge[1])
                i += 1
    return False
    


# In[141]:


diams = []
radii = []
avgpath = []
hascut = []

for i in range(10000):

    #t= get_spanning_tree_u_w(nx.grid_graph([4,5]))
    t= get_spanning_tree_u_w(nx.grid_graph([10,10]))
    tgraph=nx.Graph()
    tgraph.add_edges_from(t)
    
    diams.append(nx.diameter(tgraph))
    radii.append(nx.radius(tgraph))
    avgpath.append(nx.average_shortest_path_length(tgraph))
    hascut.append(try_balanced_cut(tgraph, 500))


# In[ ]:


diams2 = []
radii2 = []
avgpath2 = []
hascut2 = []
accept2 = []

#G= nx.grid_graph([4,5])
G = nx.grid_graph([10,10])
t= get_spanning_tree_u_w(G)
tgraph=nx.Graph()
tgraph.add_edges_from(t)
tgraphs = [tgraph]

pos = nx.kamada_kawai_layout(tgraph)#spectral_layout(G)#
for i in range(1000):
    tempT = tree_cycle_walk_cut(tgraphs[-1],G)
    
    if nx.diameter(tgraphs[-1]) < nx.diameter(tempT):
        
        tgraphs.append(tempT)
        accept2.append(1)
    else:
        if random.random() < .001:
            tgraphs.append(tempT)
            accept2.append(2)
        else:
            accept2.append(0)
            
            
    diams2.append(nx.diameter(tgraphs[-1]))
    radii2.append(nx.radius(tgraphs[-1]))
    avgpath2.append(nx.average_shortest_path_length(tgraphs[-1]))
    hascut2.append(try_balanced_cut(tgraphs[-1], 500))
            
            
            
    #tgraphs
    


# 
#
#
    
#plt.figure()
#nx.draw(tgraph,pos = {x:x for x in tgraph.nodes()})
#plt.show()


# In[114]:


plt.hist(diams)


# In[142]:


diam_vs_cut = []
hascut_bina = []
for i in hascut:
    if i == True:
        hascut_bina.append(1)
    if i == False:
        hascut_bina.append(0)
for i in range(len(diams)):
    diam_vs_cut.append((diams[i], hascut_bina[i]))


# In[145]:


counts = {}
for i in diams:
    counts.update({i:diams.count(i)})


# In[164]:


balanced_cuts_by_diam= {}
for j in range(100):
    c=0
    for i in range(len(diam_vs_cut)):
        if diam_vs_cut[i][0] == j and diam_vs_cut[i][1] == 1:
            c += 1
    balanced_cuts_by_diam.update({j:c})   
       


# In[165]:


normalized_cuts = []
for i in counts.keys():
    normalized_cuts.append((i, balanced_cuts_by_diam[i]/counts[i]))


# In[171]:


plt.scatter(*zip(*normalized_cuts))
plt.title("Percent of Plans with a Cuttable Edge vs Diameter")


# In[100]:


def try_balanced_cut(T, num_tries):
    i = 0
    while i < num_tries:
        T = T
        edge_set = set(T.edges())
        #print(edge_set)
        snip_edge = random.choice(tuple(edge_set))
        T.remove_edge(snip_edge[0], snip_edge[1])
        components = list(nx.connected_components(T))
        if len(components) == 1:
            T.add_edge(snip_edge[0], snip_edge[1])
            i += 1
        if len(components) == 2:
            if abs(len(components[0]) - len(components[1])) < 2:
                i = num_tries
                return True
            else:
                T.add_edge(snip_edge[0], snip_edge[1])
                i += 1
    return False


# In[101]:


G = nx.complete_graph(20)
t= get_spanning_tree_u_w(G)
T = nx.Graph()
node_list = [i for i in range(20)]
T.add_nodes_from(node_list)
T.add_edges_from(t)


# In[86]:


i = 0
G = nx.complete_graph(20)
t= get_spanning_tree_u_w(G)
T = nx.Graph()
node_list = [i for i in range(20)]
T.add_nodes_from(node_list)
T.add_edges_from(t)
while i < 1:
    edge_set = set(T.edges())
    snip_edge = random.choice(tuple(edge_set))
    i += 1


# In[170]:


max(diams)


# In[175]:


diam_vs_cut2 = []
hascut_bina2 = []
for i in hascut2:
    if i == True:
        hascut_bina2.append(1)
    if i == False:
        hascut_bina2.append(0)
for i in range(len(diams2)):
    diam_vs_cut2.append((diams2[i], hascut_bina2[i]))


# In[202]:


counts2 = {}
for i in diams2:
    counts2.update({i:diams2.count(i)})


# In[203]:


balanced_cuts_by_diam2= {}
for j in range(100):
    c=0
    for i in range(len(diam_vs_cut2)):
        if diam_vs_cut2[i][0] == j and diam_vs_cut2[i][1] == 1:
            c += 1
    balanced_cuts_by_diam2.update({j:c}) 


# In[204]:


normalized_cuts2 = []
for i in counts2.keys():
    normalized_cuts2.append((i, balanced_cuts_by_diam2[i]/counts2[i]))


# In[205]:


plt.scatter(*zip(*normalized_cuts2))
plt.title("Percent of Plans with a Cuttable Edge vs Diameter")


# In[180]:


normalized_cuts2


# In[210]:


len(hascut2)


# In[187]:


len(diams2)


# In[201]:


plt.hist(diams2)


# In[215]:


nx.draw(tempT)


# In[220]:


len(tgraphs)


# In[ ]:




