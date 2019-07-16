#
# An implementation of a "belief propagation algorithm"
#  (BPA) for the purpose of smoothing out gaps in urban-
#  rural information.
# This takes an initial assignment, and then at each
#  step each node simultanously updates to the most popular
#  choice of its neighbors (tiebreaks are uniform random).
#
# Original version by Daryl DeFord @ Thu Jun 27 00:11:40 2019
# Current version by Eric Stucky @ VRDI 2019
#


##########################
# Import and setup block #
##########################

import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from gerrychain import Graph
import geopandas as gpd
from collections import Counter
import random
import time
random.seed(time.time)
print("Imports complete.")

# The current code is compatible with VRDI/Your-State
#  downloaded into the same directory as this file.
# It is specific to Lousiana (FIPS code 22)
# TODO: Change the directory and/or state, as needed.

indir = "./Your-State-Master/Block_Groups/"
fips = '22'
g = Graph.from_json(indir + "BG" + fips + ".json")
df = gpd.read_file(indir + "BG" + fips + "/BG" + fips + ".shp")
print("Data loaded.")



##########################
# Global Variables Block #
##########################

URBAN = 0
RURAL = 1

nlist = list(g.nodes())

shape = True  # True -> uses geometric information to draw graphs
shuffle = True  # False -> each step updates nodes in same order
num_steps = 100



#########################
# Data Formatting Block #
#########################

# Determine where to place vertices in graphics
if shape:
    centroids = df.centroid
    c_x = centroids.x
    c_y = centroids.y
    pos = {node:(c_x[node],c_y[node]) for node in g.nodes}
else:
    pos = nx.kamada_kawai_layout(g)


# Determine initial urban-rural assignment
for n in nlist:
    if g.node[n]['URBPOP']=='0':
        g.node[n]["ur_code"] = RURAL
    else:
        selector = random.randint(1,g.node[n]['TOTPOP'])
        if selector > int(g.node[n]['URBPOP']):
            g.node[n]["ur_code"] = RURAL
        else:
            g.node[n]["ur_code"] = URBAN


# Determine which colors the ur_codes should correspond to       
def ur_color(ur_code):
    if ur_code == URBAN:
        return 'b'
    elif ur_code == RURAL:
        return 'r'
    else: # this shouldn't happen
        return '' 
    
 

###############################
# Main Loop for the Algorithm #
###############################

plots = [[] for x in range(k)]    

steps_taken = 0
for step in range(num_steps):

    # Initialize the new assignment
    new_assignment = {x:-1 for x in g.nodes()}

    if shuffle:
        random.shuffle(nlist)
        for n in nlist:
            # Count the assignments for each node's neighbors
            nassn = [g.node[neighbor]["ur_code"] for neighbor in g.neighbors(n)]
            ncount = Counter(nassn)
        
            # Determine which beliefs are most popular among
            #  neighbors; break ties randomly.
            nmax = max(ncount.values())
            nchoose = []
            for j in range(k):
                if j in nassn:
                    if ncount[j] == nmax:
                        nchoose.append(j)
            new_assignment[n] = random.choice(nchoose) 

            ## This was an attempt to break ties by staying put.
            #if ncount[0] == ncount[1]:
            #    new_assignment[n] = g.node[n]["ur_code"]
            #elif ncount[0] > ncount[1]:
            #    new_assignment[n] = 0
            #else:
            #    new_assignment[n] = 1

    # TODO: Maintain code for this alternate option.
    else:
        for n in nlist:
            nassn = [g.node[neighbor]["ur_code"] for neighbor in g.neighbors(n)]
            ncount = Counter(nassn)
            nmax = max(ncount.values())
            nchoose = []
            for j in range(k):
                if j in nassn:
                    if ncount[j] == nmax:
                        nchoose.append(j)
            
            new_assignment[n] = random.choice(nchoose)
    

    # Data visualization: 
    # Add the count data to a line chart to see the
    #  algorithm's convergence rate on this data.
    allcount = Counter(list(new_assignment.values()))   
    for j in range(k):
        if j in allcount.keys():
            plots[j].append(allcount[j])
        else:
            plots[j].append(0)
    

    # Check to see if there was any change in this step,
    #  otherwise update the assignment and iterate.
    if new_assignment == {n:g.node[x]["ur_code"] for x in nlist}:
        print("Converged")
        break
    for n in nlist:
        g.node[n]["ur_code"] = new_assignment[n] 

    ## Data visualization:
    ## Draw the intermediate graphs and their assignments
    ##  and save for future inspection.
    #nx.draw(g, pos=pos, node_size=100,
    #    node_color=[ur_color(g.node[n]["ur_code"]) for n in g.nodes()])
    #plt.savefig("somewhere.png")
    #plt.close()

    # Reassurance for impatient users.
    steps_taken += 1
    if steps_taken % 10 == 0:
        print(steps_taken, "steps taken so far.")



############################
# Data Visualization Block #
############################

# View a line chart showing how many of each belief was
#  in the assignment at each step.
# You must close this chart for the code to continue.
plt.figure()
for i in range(k):
    plt.plot([x/n for x in plots[i]],color = cmap(i),label=str(i))  
plt.legend()
plt.show()


## View the graph of the final assignment.
#nx.draw(g, pos=pos, node_size=100,
#    node_color=[ur_color(g.node[n]["ur_code"]) for n in g.nodes()])
#plt.show()


# Show how many of the nodes were uncertain in the
#  initial assignment-- and of the ones which were
#  certain, show how many retained their belief in the
#  final assignment.
definitely_wrong = 0
definitely_right = 0
ambiguous = 0
for n in nlist:
    if g.node[n]['RURALPOP'] != '0' and g.node[n]['URBPOP'] != '0':
        ambiguous += 1
    elif g.node[n]['URBPOP'] == '0':
        if g.node[n]["ur_code"] == 1:
            definitely_right += 1
        else:
            definitely_wrong += 1
    elif g.node[n]['RURALPOP'] == '0':
        if g.node[n]["ur_code"] == 0:
            definitely_right += 1
        else:
            definitely_wrong += 1
print(definitely_right, "nodes definitely right :)")
print(definitely_wrong, "nodes definitely wrong :(")
print(ambiguous, "nodes are ambiguous...")


# Scatterplot of the probability that each node was
#  initially assigned RURAL, against the binary data
#  of whether it is RURAL in the final assignment. 
# Some noise has been added to the binary coordinate
#  for easier viewing: the actual values are all either
#  0 or 1.
# You must close this plot for the code to continue.
x = []
for n in nlist:
    if g.node[n]["TOTPOP"]==0:
        x.append(-10.0)
    else:
        x.append(100.0 * int(g.node[n]["RURALPOP"])/g.node[n]["TOTPOP"])
noise = np.random.normal(0,0.15,len(nlist))
y = np.array([g.node[n]["ur_code"] for n in nlist]) + noise
plt.scatter(x,y, s=2)
plt.show()


