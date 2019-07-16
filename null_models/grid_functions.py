# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 09:46:47 2019

@author: daryl
"""

 
import networkx as nx
from random import randint, random
import matplotlib.pyplot as plt
import numpy as np
from gerrychain import Graph
from gerrychain import (
    Election,
    Graph,
    MarkovChain,
    Partition,
    accept,
    constraints,
    updaters,
)
from gerrychain.metrics import efficiency_gap, mean_median
from gerrychain.proposals import recom, propose_random_flip
from gerrychain.updaters import cut_edges
from gerrychain.tree import recursive_tree_part#, bipartition_tree_random




def rectangle_grid(n=20,m=20,k=20,ns=500,pt=True):
    grid = nx.grid_graph([n,m])
 
    unassigned = list(grid.nodes())
    rectangles = []
    
    cdict={}
    
    move = 0
    
    while unassigned:
    	
    	ll=unassigned[0]
    	uboundary = [ll]
    	rboundary = [ll]
    	unassigned.remove(ll)
    	cdict[ll]=move
    	
    	numr = 0
    	numu = 0
    	
    	
    	expands = randint(0,k)
    	
    	for i in range(expands):
    		if random() < .5:
    			#move up
    			temp = 0 
    			for j in uboundary:
    				if (j[0],j[1]+1) in unassigned:
    					temp +=1
    			if temp == len(uboundary):
    				numu += 1
    			
    				for j in range(len(uboundary)):
                        
    					if uboundary[j] in rboundary:
    						rboundary.append((uboundary[j][0],uboundary[j][1]+1))
    					
    					#grid = nx.contracted_edge(grid, (ll, (uboundary[j][0],uboundary[j][1]+1)), self_loops=False)
    
    					unassigned.remove((uboundary[j][0],uboundary[j][1]+1))
    					cdict[(uboundary[j][0],uboundary[j][1]+1)] = move
    					uboundary[j] = (uboundary[j][0],uboundary[j][1]+1)
    					grid = nx.contracted_nodes(grid, ll, (uboundary[j][0],uboundary[j][1]), self_loops=False)
    
    
    		else:
    			#move right
    			temp = 0 
    			for j in rboundary:
    				if (j[0]+1,j[1]) in unassigned:
    					temp += 1
    			if temp == len(rboundary):
    				numr += 1
                    
                    
    			
    				for j in range(len(rboundary)):
    					if rboundary[j] in uboundary:
    						uboundary.append((rboundary[j][0]+1,rboundary[j][1]))
    					unassigned.remove((rboundary[j][0]+1,rboundary[j][1]))
    					cdict[(rboundary[j][0]+1,rboundary[j][1])] = move
    					rboundary[j] = (rboundary[j][0]+1,rboundary[j][1])
    					
    					#grid = nx.contracted_edge(grid, (ll, (rboundary[j][0]+1,rboundary[j][1])), self_loops=False)
    					grid = nx.contracted_nodes(grid, ll, (rboundary[j][0],rboundary[j][1]), self_loops=False)
    
    					
    					
    					
    	rectangles.append([ll,(ll[0]+numr,ll[1]+numu)])
    	move += 1
    return grid


def walker_grid(n=20,m=20,k=20,ns=500):
    
    grid = nx.grid_graph([n,m])
     
    unassigned = list(grid.nodes())
    
    walkers=[]
    
    cdict={x:0 for x in grid.nodes()}
    
    
    for i in range(k):
        walkers.append(choice(unassigned))
        unassigned.remove(walkers[-1])
        cdict[walkers[-1]]=i+1
        
    plt.figure()
    
    nx.draw(grid,pos= {x:x for x in grid.nodes()},node_color=[cdict[x] for x in grid.nodes()],node_size=ns,cmap='tab20',node_shape='s')#cmap=plt.cm.jet,label=True)
    plt.title("Initial Walkers")
    plt.show()
    
    move = 0
    
    while unassigned:
        order = list(range(k))
        shuffle(order)
    	
        for i in order:
            old=walkers[i]
            #print(old)
            walkers[i]=choice(list(grid.neighbors(walkers[i])))
            #print(walkers[i])
            if walkers[i] in unassigned:
                unassigned.remove(walkers[i])
                cdict[walkers[i]]=i+1
                grid = nx.contracted_nodes(grid, walkers[i], old, self_loops=False)
            else:
                walkers[i]=old

    return grid

def tree_grid(n=20,m=20,k=40,varepsilon=0.01):
    graph = nx.grid_graph([n,m])


    for node in graph.nodes():
        graph.node[node]["population"] = 1
        
    cddict =  recursive_tree_part(graph,range(k),m*n/k,"population", varepsilon,1)
        
    updater = {
    "cut_edges": cut_edges
    }

    initial_partition = Partition(graph,cddict, updater)
    
    dg=nx.Graph()
    for edge in initial_partition["cut_edges"]:
        dg.add_edge(cddict[edge[0]],cddict[edge[1]])
        
    return dg
    


    
    
    