##########################
# Import and Setup Block #
##########################

import networkx as nx
import pandas as pd
import os
import json
from networkx.readwrite import json_graph
from gerrychain import Graph
import geopandas as gpd
from geopandas import GeoSeries
import itertools
from itertools import combinations
from shapely.geometry import (
    Polygon,
    Point
) 

import matplotlib.pyplot as plt

print("Imports Complete.")
print()



##########################
# Global Variables Block #
##########################

LEVEL = "COUSUB"
IMG_DPI = 300

# TODO: Adjust to your file system
indir_graph = "./Your-State-master/" + LEVEL + "/dual_graphs/"
indir_df = "./Census_Shapefiles/Census_Shapefiles/" + LEVEL + "/"
outdir = "./faceshape_statistics/"

fips_list = []
tri_list = []
rect_list = []
#rect_radius_list = []  # for future implementation
#rect_diameter_list = []
rect_largest_comp_list = []
rect_num_comp_list = []

rect_percent_list = []



###########################
# Graphs Definition Block #
###########################

def face_graphs(input_graph, df):
    '''
    Input:  input_graph is a planar networkx graph,
            df is a geopandas dataframe
    Output: Two networkx graphs, tgraph and rgraph.
            These record the set of 3- and 4-faces
            (respectively) of input_graph.
    There are known issues with rgraph for pathological
    geometries, especially when nonplanarities arise;
    see VRDI 2019 Week 5 Slideshow images for examples. 
    '''

    #-----------------------------#
    # Defining Variables Subblock #
    #-----------------------------#

    centroids = df.centroid
    c_x = centroids.x
    c_y = centroids.y
    pos = {node:(c_x[node],c_y[node]) for node in input_graph.nodes}
    pts = GeoSeries([Point(px, py) for px, py in pos.values()])

    # triangule graph variables
    tgraph = nx.Graph()
    copy1 = input_graph.copy()
    edges = list(copy1.edges)
    nodes = copy1.nodes

    # rectangle graph variables 
    rgraph = nx.Graph()
    copy2 = input_graph.copy()
    nodes2 = list(copy2.nodes)


    #-------------------------#
    # Triangle Graph Subblock #
    #-------------------------#

    # For each edge (a,b) find the common neighbors c of its
    #  endpoints. If there are no extra points inside, then
    #  this is a face.
    # The elif statement handles some corner cases; see the
    #  comments in the Rectangle Graph Subblock for the
    #  general issue. In particular, this case is when a
    #  two triangles share a common edge and the third point
    #  of one is inside the other: this produces a 4-face
    #  which would not otherwise be counted. 
    counter = 0
    for (a,b) in edges:
        third_point = [x for x in copy1.neighbors(a) if x in copy1.neighbors(b)]
        for c in third_point:
            axy = pos[a]
            bxy = pos[b]
            cxy = pos[c]  
            triangle = Polygon([axy, bxy, cxy])   
                            
            if pts.intersects(triangle).sum() == 3:
                tgraph.add_node((a,b,c)) 
            elif pts.intersects(triangle).sum() == 4:
                for i in range (len(nodes)):
                    if pts.intersects(triangle).iloc[i]:
                        if i != a and i != b and i != c:
                            L = [x for x in [a,b,c] if x in copy1.neighbors(i)]
                            if len(L) == 2:
                                rgraph.add_node((i, a, b, c))
        copy1.remove_edge(a,b)
        counter += 1
        if counter % 1000 == 0:
            print(counter, "edges considered")
    
    # Edges in the tgraph denote edge-adjacencies of triangles.
    for i,j in combinations(list(tgraph.nodes),2):
        if len(set(i+j))<5:       # if triangles disjoint, have six vertices
            tgraph.add_edge(i,j)  # between them, so <5 guarantees at least edge
                                  # have at least an edge, and 
    
    # Locate the nodes of tgraph at the centroid of the four points
    for triangle in tgraph.nodes:
        axy = pos[triangle[0]]
        bxy = pos[triangle[1]]
        cxy = pos[triangle[2]]
        posx = (axy[0]+bxy[0]+cxy[0])/3
        posy = (axy[1]+bxy[1]+cxy[1])/3
        tgraph.nodes[triangle]["pos"] = (posx, posy)
    
    print("tgraph created")


    #--------------------------#
    # Rectangle Graph Subblock #
    #--------------------------#

    # For each vertex n and each pair of its neighbors i,j
    #  find their common neighbors k. If the diagonal edges
    #  are missing and there are no extra points inside,
    #  then this is a face.
    # Note in particular that one diagonal edge can be
    #  present while still having a quadrilateral face, if
    #  that face is non-convex! So this loop will always
    #  undercount the number of 4-faces. 
    # Some of these faces are caught in the Triangle Graph
    #  Subblock above, but others will not be.
    counter = 0
    for n in nodes2:
        nhlist=list(copy2.neighbors(n))
        for i,j in combinations(nhlist,2):
            if (i,j) not in copy2.edges():
                for k in copy2.neighbors(i):
                    if k != n:
                        if (j,k) in copy2.edges() and (n,k) not in copy2.edges():
                            nxy = pos[n] 
                            ixy = pos[i]
                            jxy = pos[j]
                            kxy = pos[k]      
                            square = Polygon([nxy, ixy, kxy, jxy])    
                            
                            if pts.intersects(square).sum() == 4:
                                rgraph.add_node((n,i,j,k))     
        copy2.remove_node(n)
        counter += 1
        if counter % 1000 == 0:
            print(counter, "nodes considered")

    # Edges in the rgraph denote edge-adjacencies of rectangle.
    # The <7 is analogous to the <5 condition explained in the
    #  Triangle Graph Subblock.
    for i,j in combinations(list(rgraph.nodes),2):
        if len(set(i+j))<7:
            rgraph.add_edge(i,j)
    print("rgraph created")

    # Locate the nodes of rgraph at the centroid of the four points
    for square in rgraph.nodes:
        axy = pos[square[0]]
        bxy = pos[square[1]]
        cxy = pos[square[2]]
        dxy = pos[square[3]]
        posx = (axy[0]+bxy[0]+cxy[0]+dxy[0])/4
        posy = (axy[1]+bxy[1]+cxy[1]+dxy[1])/4
        rgraph.nodes[square]["pos"] = (posx, posy)


    return rgraph, tgraph



##########################
# Helper Functions Block #
##########################

def face_statistics(rgraph, tgraph):
    #faces = len(input_graph.edges) - len(input_graph.nodes) + 1
    faces = len(rgraph.nodes) + len(tgraph.nodes)
    if faces == 0:
        return -1, -1
    else:
        percent_tri = 100.0 * len(tgraph.nodes) / faces
        percent_rect = 100.0 * len(rgraph.nodes) / faces
        return percent_rect, percent_tri

    
def draw_with_location(graph,c='k',ns=100,w=3,ec='b'):
#    for x in graph.nodes():
#        graph.node[x]["pos"] = [graph.node[x]["X"], graph.node[x]["Y"]]

    nx.draw(graph, pos=nx.get_node_attributes(graph, 'pos'), 
            node_size = ns, width = w, node_color=c,edge_color=ec)



#############
# MAIN LOOP #
#############

#for state in list(range(1,1+56)) + [72]:  # all FIPS codes
for state in [19,25,5]:
    # ignore invalid FIPS codes:
    if state in [3,7,14,36,43,52]:
        continue
    #else

    #--------------------------#
    # Data Formatting Subblock #
    #--------------------------#

    statecode = str(state).zfill(2)  # makes 'state' into a 2-digit string
    levelcode = LEVEL + statecode
    g = Graph.from_json(indir_graph + levelcode + ".json")
    df = gpd.read_file(indir_df + levelcode + ".shp")

    centroids = df.centroid
    c_x = centroids.x
    c_y = centroids.y
    pos = {node:(c_x[node],c_y[node]) for node in g.nodes}

    #--------------------------#
    # Graph-Building Subblock  #
    #  (see face_graphs above) # 
    #--------------------------#

    print("generating graphs for FIPS " + statecode)
    rgraph, tgraph = face_graphs(g, df)


    #-------------------#
    # Output Subblock I #
    #-------------------#

    # TODO: A lot of magic numbers here.
    # Trying to adjust the sizes of vertices as the vertices get
    #  closer together, using IMG_DPI as a proxy for this.

    # Rectangle graph variables
    # Creates the relevant directories, if needed.
    rpath_json = outdir + "graphs/" + levelcode + "_rgraph.json"
    rpath_png = outdir + "images/" + levelcode + "_rgraph.png"
    os.makedirs(os.path.dirname(rpath_json), exist_ok=True)
    os.makedirs(os.path.dirname(rpath_png), exist_ok=True)

    # Draws a picture of the LEVEL geography, plus the
    #  corresponding dual graph and its rectangle graph
    #  overlayed.
    # Replace the first line with plt.figure() to output the
    #  graph without the underlying geometry.
    df.plot(edgecolor='w',linewidth=2 * 300.0/IMG_DPI, facecolor='lime')
    nx.draw(g, node_size=25 * (300.0/IMG_DPI)**3, width= 300.0/IMG_DPI, pos=pos)
    draw_with_location(rgraph, 'r',25 * (300.0/IMG_DPI)**3, 300.0/IMG_DPI,'r')
    plt.savefig(rpath_png, dpi=IMG_DPI)
    plt.close()

    # Saves rgraph as a JSON file for later processing.
    with open(rpath_json, "w") as f:
        json.dump(json_graph.node_link_data(rgraph), f)


    # Triangle graph variables
    # Creates the relevant directories, if needed.
    tpath_json = outdir + "graphs/" + levelcode + "_tgraph.json"
    tpath_png = outdir + "images/" + levelcode + "_tgraph.png"
    os.makedirs(os.path.dirname(tpath_json), exist_ok=True)
    os.makedirs(os.path.dirname(tpath_png), exist_ok=True)

    # Draws a picture of the LEVEL geography, plus the
    #  corresponding dual graph and its triangle graph
    #  overlayed.
    # Replace the first line with plt.figure() to output the
    #  graph without the underlying geometry. 
    df.plot(edgecolor='w',linewidth=2 * 300.0/IMG_DPI, facecolor='lime')
    nx.draw(g, node_size=25 * (300.0/IMG_DPI) ** 3, width= 300.0/IMG_DPI, pos=pos)
    draw_with_location(tgraph, 'r',25* (300.0/IMG_DPI) ** 3, 300.0/IMG_DPI,'r')
    plt.savefig(tpath_png, dpi=IMG_DPI)
    plt.close()

    # Saves tgraph as a JSON file for later processing.
    with open(tpath_json, "w") as f:
        json.dump(json_graph.node_link_data(tgraph), f)
    

    #---------------------------------------#
    # Output Subblock II:                   #
    #  Global Output (for use outside loop) #
    #---------------------------------------#

    fips_list.append(statecode)
    tri_list.append(len(tgraph.nodes))
    rect_list.append(len(rgraph.nodes))
    rect_num_comp_list.append(nx.number_connected_components(rgraph))
    if len(rgraph.nodes) == 0:
        rect_largest_comp_list.append(0)
    else:
        big_comp = len(max(nx.connected_components(rgraph), key=len))
        rect_largest_comp_list.append(big_comp)

    trash,data = face_statistics(rgraph,tgraph)


    print("data saved")
    print()
    # loop complete



######################################
# Processing and Visualization Block #
######################################

# Save some basic statistics from the graphs created by the
#  for-loop for processing later.
stats = pd.DataFrame({
    "FIPS": fips_list,
    "N-TRIANGLES": tri_list,
    "N-RECTANGLES": rect_list,
    #"RECT-RADIUS": rect_radius_list,  # for future implementation
    #"RECT-DIAMETER": rect_diameter_list, 
    "RECT-LARGEST-COMP": rect_largest_comp_list,
    "RECT-NUM-COMP": rect_num_comp_list,
})
stats.to_csv(outdir + "stats.csv", index=False)

# Visualization: note that this assumes that the algorithm
#  catches all faces, which it does not. However, it at
#  least serves to compare the approximate ratio of 4-faces
#  to 3-faces (approximate because of the 4-face errors)
#  described in the MAIN LOOP.
plt.figure()
plt.hist(data, bins=20, range=(0,100))
plt.savefig("./percent_rect.png")
plt.close()

