# -*- coding: utf-8 -*-
"""
This code is and adaptation of Daryl DeFord belief_prop.py by Cleveland Waddell
at VRD! 2019
"""
import shutil
import os
import urllib.request
import pickle
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import random
import numpy as np
from gerrychain import Graph
import geopandas as gpd
from collections import Counter

acc_list = []
fips_list = []

for d1 in range(10):
    for d2 in range(10):
        if str(d1)+str(d2) in ["00","03","07","14","43","52","06","12","17"] or d1==5 and d2>6:
        
            continue
        else:

            bg_fips = "BG"+str(d1)+str(d2)
"""
The Block json can be read directly from the vrdi git hub using the commented code that follows
"""            
###            url = "https://raw.githubusercontent.com/vrdi/Your-State/master/Block_Groups/"+bg_fips+".json"
###            directory = "/home/cleveland/Desktop/VRDI2/My_State/NetworksWeek5/UvR/BG_Json/"
###            filename = directory + bg_fips+".json"
###            urllib.request.urlretrieve(url, filename)
###            g = Graph.from_json(filename)
            g = Graph.from_json("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/Your-State/Block_Groups/"+bg_fips+".json")
            df = gpd.read_file("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BG/"+bg_fips+".shp")
            centroids = df.centroid
            c_x = centroids.x
            c_y = centroids.y
            shape = True

            nlist = list(g.nodes())
            n = len(nlist)

### shuffle = True
            shuffle = False

            num_steps = 100

            pos = nx.kamada_kawai_layout(g)
            if shape:
                pos = {node:(c_x[node],c_y[node]) for node in g.nodes}


            k = 2

            for n in nlist:
                urb_pop = int(g.node[n]["URBPOP"])
                rur_pop = int(g.node[n]["RURALPOP"])
                if urb_pop > 0 and rur_pop == 0:
                    g.node[n]["cddict"] = 0 ### assign 0 to node if it has only urban pop
                elif rur_pop > 0 and urb_pop == 0:
                    g.node[n]["cddict"] = 1 ### assign 1 to node if it has only rural pop
                else:
                    g.node[n]["cddict"] = random.choice([0,1])
        
            nx.draw(g,pos=pos,node_color=[g.node[x]["cddict"] for x in nlist],node_size=25)
            
            plt.savefig(f"/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/step_init_"+bg_fips+".png")
    
 
            plots = [[] for x in range(k)]    

            for step in range(num_steps):
                new_assignment = {x:-1 for x in g.nodes()}
    
                if shuffle:
                    random.shuffle(nlist)
                    for n in nlist:
                        if g.degree[n] == 0:
                            continue
                        nassn = [g.node[neighbor]["cddict"] for neighbor in g.neighbors(n)]
                        ncount = Counter(nassn)
        
                        nmax = max(ncount.values())
                        nchoose = []
                        for j in range(k):
                            if j in nassn:
                                if ncount[j] == nmax:
                                    nchoose.append(j)
            
                        new_assignment[n] = random.choice(nchoose)
        
                else:
                    for n in nlist:
                        if g.degree[n] == 0:
                            continue
                        nassn = [g.node[neighbor]["cddict"] for neighbor in g.neighbors(n)]
                        ncount = Counter(nassn)
                        nmax = max(ncount.values())
                        nchoose = []
                        for j in range(k):
                            if j in nassn:
                                if ncount[j] == nmax:
                                    nchoose.append(j)
            
                        new_assignment[n] = random.choice(nchoose)
        
                allcount = Counter(list(new_assignment.values()))   
                for j in range(k):
                    if j in allcount.keys():
                        plots[j].append(allcount[j])
                    else:
                        plots[j].append(0)
                if new_assignment == {n:g.node[x]["cddict"] for x in nlist}:
                    print("Converged")
                    break
        
    
                for n in nlist:
                    g.node[n]["cddict"] = new_assignment[n]
    
                if step % 10 == 0:
                    nx.draw(g,pos=pos,node_color=[g.node[x]["cddict"] for x in nlist],node_size=25)
                
                    plt.savefig(f"/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/step{step:03d}"+bg_fips+".png")
                    plt.close()
                    if shape:
                        df["infect"] = df.index.map({x:g.node[x]["cddict"] for x in nlist})
                        df.plot(column = "infect")
            
                        plt.savefig(f"/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/dfstep{step:03d}"+bg_fips+".png")
                        plt.close()
    
    
            cmap = matplotlib.cm.get_cmap('tab20')
            
            for n in nlist:
                tot_pop = int(g.node[n]["TOTPOP"])
                if tot_pop == 0:
                    g.node[n]["uvr"] = 1
                elif urb_pop/tot_pop > 0.5:
                    g.node[n]["uvr"] = 0
                else:
                    g.node[n]["uvr"] = 1
        
            count = 0
            for n in nlist:
                if  g.node[n]["uvr"] == g.node[n]["cddict"]:
                    count = count + 1
        
            pct_acc = count/len(nlist)

            plt.figure()
            acc_list.append(pct_acc)
            fips_list.append(bg_fips)
            y_pos = np.arange(len(fips_list))
            plt.bar(y_pos, acc_list, align='center', alpha=0.5)
            plt.xticks(y_pos, fips_list)
            plt.ylabel('Performance')
            plt.title('States Performace in belief prop')
            
            plt.savefig("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/votebar.png")
            plt.close()
            