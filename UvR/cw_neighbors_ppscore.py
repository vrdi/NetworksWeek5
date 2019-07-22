"""
This code is and adaptation of Daryl DeFord belief_prop.py.
It uses bounds uptained from analysing the results of ppvstat.py
to make an initial assignment of urban block groups and rural
block groups. We the run belief_prop.py. 
The output of the code is a bar chart that compares this method
accross states. The code also produces a graph where the nodes 
are colored according to their PolsbyPopper_score. 
"""
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import random
import math
from gerrychain import Graph
from gerrychain import GeographicPartition
from gerrychain.metrics import polsby_popper
import geopandas as gpd
from collections import Counter

acc_list = []
fips_list = []
state_pp_list = []
state_area_list = []
for d1 in range(10):
    for d2 in range(10):
   
        bg_urb_pop_list =[]
        bg_pct_urb_list = []
        bg_area_list = []
        
        if str(d1)+str(d2) in ["00","03","07","14","43","52","06","12","17"] or d1==5 and d2>6:
            continue
        else:
            bg_fips = "BG"+str(d1)+str(d2)
            g = Graph.from_json("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/Your-State/Block_Groups/"+bg_fips+".json")
            df = gpd.read_file("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BG/"+bg_fips+".shp")
            centroids = df.centroid
            c_x = centroids.x
            c_y = centroids.y
            shape = True

            nlist = list(g.nodes())
            n = len(nlist)

            shuffle = False
            num_steps = 10

            pos = nx.kamada_kawai_layout(g)
            if shape:
                pos = {node:(c_x[node],c_y[node]) for node in g.nodes}
                
            unique_id = 0    
            for n in nlist:
                g.node[n]["PP_ID"] = unique_id
                unique_id += 1
            
            pp_dic = GeographicPartition(g, "PP_ID", {"pp":polsby_popper})
            
            bg_pp_list = list(pp_dic["pp"].values())
            k = 2
            for n in nlist:
                if bg_pp_list[n] > 0.8:
                    g.node[n]["cddict"] = 0
                elif bg_pp_list[n] < 0.1:
                    g.node[n]["cddict"] = 1
                else:
                    g.node[n]["cddict"] = random.choice([0,1])


            nx.draw(g,pos=pos,node_color=[g.node[x]["cddict"] for x in nlist],node_size=25)

            plt.savefig("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/step_init_pp"+bg_fips+".png")
    
 
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
                    
                    plt.savefig(f"/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/step{step:03d}"+bg_fips+"pp.png")
                    plt.close()
                    if shape:
                        df["infect"] = df.index.map({x:g.node[x]["cddict"] for x in nlist})
                        df.plot(column = "infect")
                        
                        plt.savefig(f"/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/dfstep{step:03d}"+bg_fips+"pp.png")
                        plt.close()
    
    
            cmap = matplotlib.cm.get_cmap('tab20')
            
            for n in nlist:
                urb_pop = int(g.node[n]["URBPOP"])
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
            plt.savefig(f"/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/ppbar{d1}.png")
            plt.close()               
            