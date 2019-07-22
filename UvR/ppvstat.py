import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
from gerrychain import Graph
from gerrychain import GeographicPartition
from gerrychain.metrics import polsby_popper
import geopandas as gpd

state_pp_list = []
state_area_list = []
for d1 in range(10): # First digit of fips code
    for d2 in range(10): #Second digit in fips code
        bg_urb_pop_list =[]
        bg_pct_urb_list = []
        bg_area_list = []
        #if d1==0 and d2==0 or d1==0 and d2==3 or d1==0 and d2==7 or d1==1 and d2==4 or d1==4 and d2==3 or d1==5 and d2==2 or d1==5 and d2>6 or d1==0 and d2==6 or d1==1 and d2==2 or d1==1 and d2==7:
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
###            num_steps = 10

            pos = nx.kamada_kawai_layout(g)
            if shape:
                pos = {node:(c_x[node],c_y[node]) for node in g.nodes}
                
            unique_id = 0    
            for n in nlist:
                bg_area_list.append(g.node[n]["Shape_area"])
                urb_pop = int(g.node[n]["URBPOP"])
                tot_pop = int(g.node[n]["TOTPOP"])
                if tot_pop == 0:
                    bg_pct_urb_list.append(0)
                else:
                    bg_pct_urb_list.append(urb_pop/tot_pop)
                bg_urb_pop_list.append(urb_pop)
                g.node[n]["PP_ID"] = unique_id
                unique_id += 1
            
            pp_dic = GeographicPartition(g, "PP_ID", {"pp":polsby_popper})
            #bg_pp_list.append(pp_dic.value(x) for x in pp_dic)
            bg_pp_list = list(pp_dic["pp"].values())
            nx.draw(g, pos=pos, node_color=bg_pp_list, node_size=25)
            plt.savefig("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/node_pp_score"+bg_fips+".png")
            plt.close()
            #plt.scatter(bg_area_list, bg_pp_list)
            #plt.show()
            #plt.savefig("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/ppvarea"+bg_fips+".png")
            #plt.scatter(bg_urb_pop_list, bg_pp_list)
            #plt.show()
            #plt.savefig("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/ppvurbpop"+bg_fips+".png")
            #state_pp_list.append(pp_dic["pp"])
            plt.figure()
            plt.hist(bg_pp_list)
            plt.title("Polsby Popper Scores for block groups"+bg_fips)
            plt.savefig("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/ppvhist"+bg_fips+".png")
            plt.close()
            #plt.show()
            #plt.scatter([math.log(x) for x in bg_area_list], bg_pp_list)
            #plt.savefig("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/ppvlogarea"+bg_fips+".png")
            #plt.show()
            plt.figure()
            plt.scatter(bg_pct_urb_list, bg_pp_list)
            plt.title('Polsby Popper Score vs Pct Urban for Block Groups'+bg_fips)
            plt.xlabel('Pct Urban')
            plt.ylabel('Polsby Popper Score')
            plt.savefig("/media/cleveland/ea722593-dc05-41aa-8b50-9ac3c60c0aa7/Census_Shapefiles/Census_Shapefiles/BPplots/ppvurbpct"+bg_fips+".png")
            plt.close()
            #plt.show()