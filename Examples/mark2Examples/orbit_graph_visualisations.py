if __name__ == '__main__':
    from _example_path_tools import add_path_examples
    add_path_examples()

from permutation import Permutation
from group import PermGroup
from orbit_graph import OrbitGraph
from graph_visualisation import draw_orbit_graph

def vis_klien4():
    a = Permutation.read_cycle_form([[1,2],[3,4]],4)
    b = Permutation.read_cycle_form([[1,3],[2,4]],4)
    G = PermGroup([a,b])
    oG = OrbitGraph(G,(1,2))
    draw_orbit_graph(oG)
    
def vis_cyclic6():
    b = Permutation.read_cycle_form([[1,2,3,4,5,6]],6)
    G = PermGroup([b])
    oG = OrbitGraph(G,(1,2))
    draw_orbit_graph(oG)
    
def vis_S3_cross_Z3():
    cf = Permutation.read_cycle_form
    a = cf([[4,5]],6)
    b = cf([[5,6]],6)
    c = cf([[1,2,3]],6)
    G = PermGroup([a,b,c])
    oG = OrbitGraph(G,(4,2))
    draw_orbit_graph(oG)    


#vis_klien4()
#vis_cyclic6()
vis_S3_cross_Z3()