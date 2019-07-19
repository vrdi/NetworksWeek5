#!/usr/bin/env python
# coding: utf-8

# In[33]:


# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 09:53:30 2019
@author: daryl
"""


#from hamming import greedy_hamming
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import scipy as sp

from functools import partial

from sklearn import manifold
from sklearn.metrics import euclidean_distances
from sklearn.decomposition import PCA
from gerrychain import (Graph, constraints, MarkovChain, accept, updaters)
import geopandas as gpd
from gerrychain.tree import recursive_tree_part
from gerrychain.partition import Partition
from gerrychain.updaters import Tally, cut_edges
from gerrychain.updaters import Election
from gerrychain.metrics import efficiency_gap, mean_median
from gerrychain.proposals import flip, recom, propose_random_flip
from gerrychain.constraints import single_flip_contiguous
import random
import time
import networkx as nx
import math


# In[28]:


start_time = time.time()
graph_path = "./PA_VTD.json"
data_path = "./PA_VTD.shp"
#graph_path = "../diffusion/vrdi-graphs/iowa.json"
#data_path = "../diffusion/vrdi-graphs/IA-shapefiles/IA_counties/IA_counties.shp"
g = Graph.from_json(graph_path)
df = gpd.read_file(data_path)
centroids = df.centroid
c_x = centroids.x
c_y = centroids.y
shape = True

nlist = list(g.nodes())
n = len(nlist)

totpop = 0
for node in g.nodes():
    g.node[node]["TOT_POP"]=int(g.node[node]["TOT_POP"])

    totpop += g.node[node]["TOT_POP"]
    
    if int(g.node[node]["T16PRESD"]) == 0:
        g.node[node]["DEM_PCT"] = 0
    else:
        g.node[node]["DEM_PCT"] = int(g.node[node]["T16PRESD"])/(int(g.node[node]["T16PRESR"]) + int(g.node[node]["T16PRESD"]))
    g.node[node]["centroid"] = (c_x[node], c_y[node])
    

if shape:
    pos = {node:(c_x[node],c_y[node]) for node in g.node}


# In[41]:


dists = np.zeros((len(g.node), len(g.node)))
s = 0.5
for node1 in g.node:
    for node2 in g.node:
        temp_geo = math.sqrt((g.node[node1]['centroid'][0] - g.node[node2]['centroid'][0])**2 + (g.node[node1]['centroid'][1] - g.node[node2]['centroid'][1])**2)
        temp_partisan = abs(g.node[node1]["DEM_PCT"] - g.node[node2]["DEM_PCT"])
        temp = s*temp_geo + temp_partisan
        dists[node1, node2] = temp


# In[46]:


partisan = np.zeros((len(g.node), len(g.node)))
for node1 in g.node:
    for node2 in g.node:
        temppart = abs(g.node[node1]["DEM_PCT"] - g.node[node2]["DEM_PCT"])
        partisan[node1, node2] = temppart


# In[50]:


geo_dists = np.subtract(dists, partisan)
geo_dists = 2*geo_dists


# In[53]:


geo_dists


# In[54]:


partisan


# In[55]:


another_dists = np.add(0.1*geo_dists, partisan)


# In[56]:


another_dists


# In[22]:


cddicts = []

num_cong_dists = 18

num_trees = 0
for i in range(num_trees):
    cddicts.append(recursive_tree_part(g,range(num_cong_dists),totpop/num_cong_dists,"TOT_POP", .02,1))
    
ideal_population = totpop/num_cong_dists
    
proposal = propose_random_flip   

def cut_length(partition):
    return len(partition["cut_edges"])


num_flips = 5
num_flip_steps = 1000



def step_num(partition):
    parent = partition.parent
    if not parent:
        return 0
    return parent["step_num"] + 1

def b_nodes_bi(partition):
    return {x[0] for x in partition["cut_edges"]}.union({x[1] for x in partition["cut_edges"]})   



def cut_length(partition):
    return len(partition["cut_edges"])

updater = {
    "population": updaters.Tally("TOT_POP"),
    "cut_edges": cut_edges,
    "step_num": step_num,
    'b_nodes': b_nodes_bi
}



initial_partition = Partition(g, "GOV", updater)


compactness_bound = constraints.UpperBound(
    cut_length,  cut_length(initial_partition)
)

cols=["GOV","TS", "REMEDIAL_P", "538CPCT__1", "538DEM_PL", "538GOP_PL","8THGRADE_1"]

#flipdicts = []
#for d in range(num_flips):

    #chain = MarkovChain(
        #proposal=proposal,
        #constraints=[
             #single_flip_contiguous #constraints.within_percent_of_ideal_population(initial_partition, 0.2),
            #compactness_bound #no_more_discontiguous
        #],
        #accept=accept.always_accept,
        #initial_state=initial_partition,
        #total_steps=num_flip_steps,
    #)


    #t = 0
    #for part in chain:
        #t += 1
        #if t == 1000:
            #flipdicts.append(part)


Parts=[] # Partition(g,cddicts[i],updater) for i in range(num_trees)
#for flip_plan in flipdicts:
    #Parts.append(flip_plan)
for col in cols:
    Parts.append(Partition(g,col,updater))


#for i in range(num_trees):
    #cols.insert(0,f'Tree{i}')


a = np.zeros([len(Parts),len(Parts)])

def pop_dev(part):
    pops = list(part["population"].values())
    return (np.max(pops)-np.min(pops))/np.sum(pops)


# In[8]:


#def distance_between(part1,part2):
    
    #tempnames,ham = diffusion_distance(part1,part2)
    #return ham



    
    
    
    #return abs(len(part1["cut_edges"])-len(part2["cut_edges"]))/len(g.edges()) + abs(pop_dev(part1)-pop_dev(part2))
    #return abs(np.max(list(part1["population"].values()))-np.max(list(part2["population"].values())))
    
    #return 1/(1+len(part1['b_nodes'].intersection(part2['b_nodes'])))
    
    #return abs(mean_median(part1["SEN16"])-  mean_median(part2["SEN16"])) + abs(efficiency_gap(part1["SEN16"])-  efficiency_gap(part2["SEN16"]))
    
    #a1=sorted(part1["SEN16"].percents("DEM"))
    #a2=sorted(part2["SEN16"].percents("DEM"))
    
    
    
    #return sum([abs(a1[x]-a2[x]) for x in range(len(a1))])
      
    
    
    


#for i in range(len(Parts)):
    #for j in range(len(Parts)):
        #if i>j:
            #temp = some distance
            #a[i,j]=temp
            #a[j,i]=temp
    #print("partition " + str(i))




mds = manifold.MDS(n_components=2, max_iter=3000, eps=.00001, 
                   dissimilarity="precomputed", n_jobs=1)


print("mds done")

pos = mds.fit(a).embedding_

print("embedding done")

plt.figure()
for i in range(len(pos)):
    if i<num_trees:
        plt.plot(pos[i][0], pos[i][1], 'o', color = 'k', markersize=10)
    elif num_trees <= i and i < (num_trees + num_flips):
        plt.plot(pos[i][0], pos[i][1], 'o', color = 'red', markersize = 10)
    else:
        plt.plot(pos[i][0],pos[i][1],'o',label=cols[i],markersize=10)
plt.plot([],[],'o',color='k',label="Trees",markersize=10)
plt.plot([],[],'o', color = 'red', label = "Flips", markersize = 10)
plt.legend()    
plt.show()


print("finished in:", time.time()-start_time, "seconds")


"""
a = np.zeros([10,10])
for i in range(10):
    for j in range(10):
        if i>j:
            temp = random.random()
            a[i,j]=temp
            a[j,i]=temp
            
"""


# In[9]:


initial_partition


# In[23]:


pop_dev(initial_partition)


# In[21]:





# In[31]:


len(g.node)


# In[42]:


mds = manifold.MDS(n_components=2, max_iter=3000, eps=.00001, 
                   dissimilarity="precomputed", n_jobs=1)


print("mds done")

pos = mds.fit(dists).embedding_

print("embedding done")

plt.figure()
for i in range(len(pos)):
    plt.plot(pos[i][0],pos[i][1],'o', markersize=10)
#plt.plot([],[],'o',color='k',label="Trees",markersize=10)
#plt.plot([],[],'o', color = 'red', label = "Flips", markersize = 10)
plt.legend()    
plt.show()


# In[44]:


plt.figure()
for i in range(len(pos)):
    plt.plot(pos[i][0],pos[i][1],'o', markersize=2)
#plt.plot([],[],'o',color='k',label="Trees",markersize=10)
#plt.plot([],[],'o', color = 'red', label = "Flips", markersize = 10)
plt.legend()    
plt.show()


# In[ ]:


another_pos = mds.fit(another_dists).embedding_

print("embedding done")

plt.figure()
for i in range(len(another_pos)):
    plt.plot(another_pos[i][0],another_pos[i][1],'o', markersize=2)
#plt.plot([],[],'o',color='k',label="Trees",markersize=10)
#plt.plot([],[],'o', color = 'red', label = "Flips", markersize = 10)
plt.legend()    
plt.show()


# In[ ]:




