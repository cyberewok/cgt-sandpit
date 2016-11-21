import networkx as nx
import matplotlib.pyplot as plt

def draw_orbit_graph(o_graph):   
    G=nx.DiGraph()
    #G.add_labeled_nodes_from(range(1,7))
    G.add_edges_from(o_graph.edges)
    
    pos=nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos)
    nx.draw_networkx_edges(G,pos,arrows=True)
    nx.draw_networkx_labels(G,pos)
    plt.axis('off')
    plt.show() # display