#
# Code for getting nationwide data comparing the urban/rural
#  population counts to the area and density of the
#  associated block groups.
# Eric Stucky @ VRDI 2019
#
# Contains a wrapper for generally getting information from
#  most states using the data from the VRDI/Your-State repo
#  (apparently: not including New York #36; including
#   Puerto Rico #72 but not Puerto Rico #43)
# Some minimal instructions are included in comments.
#

################
# Import block #
################

import matplotlib.pyplot as plt
import networkx as nx
import math
from gerrychain import Graph


# TODO: Download VRDI/Your-State into the same folder
#        as this file, and then
#     : Change outdir to the folder where the output
#        should wind up being saved.
indir = "./Your-State-Master/Block_Groups/"
outdir = "./UR_plot_outputs/"

#present: 1–56, plus 72
#missing: 3,7,14,36,43,52
for state in list(range(1,1+56)) + [72]:
    if state in [3,7,14,36,43,52]:
        continue
    #else
    statecode = str(state).zfill(2)
    graph = Graph.from_json(indir + "BG" + statecode + ".json")

    # Warning: As written, islands are not handled by this:
    # the terminal may throw warnings. If your code is
    # sensitive to islands, you should do further preprocessing.

    ############################
    # The 'do-the-thing' Block #
    # TODO: Change this code!  #
    ############################

    pcts_rural = []
    densities = []
    areas = []

    for i in graph.nodes():
        node = graph.nodes()[i]
        if node['RURALPOP'] != '0' and node['URBPOP'] != '0':
            pct = 100 * float(node['RURALPOP']) / node['TOTPOP']
            dens = node['TOTPOP']/node['area']

            pcts_rural.append(pct)
            densities.append(math.log(dens))
            areas.append(math.log(node['area']))

    ############################
    # Data Visualization Block #
    # TODO: Change this code!  #
    ############################

    #plt.hist(pcts_rural, bins=[2.5*i for i in range(41)])
    plt.scatter(pcts_rural, areas)
    plt.title('Block Group Level Analysis')
    plt.xlabel('Percent Rural Population (0 & 100 excluded)')
    plt.ylabel('log(Area)')
    plt.savefig(outdir + 'UR_vs_area_' + statecode + '.png')
    plt.close()

    plt.scatter(pcts_rural, densities)
    plt.title('Block Group Level Analysis')
    plt.xlabel('Percent Rural Population (0 & 100 excluded)')
    plt.ylabel('log(Density)')
    plt.savefig(outdir + 'UR_vs_dens_' + statecode + '.png')
    plt.close()
