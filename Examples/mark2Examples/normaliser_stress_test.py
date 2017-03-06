if __name__ == '__main__':
    import _example_path_tools


from permutation import Permutation
from group import PermGroup
from leon_preset import symmetric_normaliser
from leon_logger import NodeCounter

def norm_example_1():
    tracker = NodeCounter()
    size = 25
    cf = lambda x: Permutation.read_cycle_form(x, size)
    a = cf([[1,2],[7,10,8]])
    b = cf([[1,2,3,4,5],[8,9,10,11,12],[13,14,15,16,17,18,19]])
    G = PermGroup([a,b])
    norm = symmetric_normaliser(G, [tracker])
    print(G.order())
    print(norm.order())
    print(norm.order()/G.order())
    print(tracker)
    
def norm_example_2():
    tracker = NodeCounter()
    size = 11
    cf = lambda x: Permutation.read_cycle_form(x, size)
    a = cf([[1,2],[7,10,8]])
    b = cf([[1,2,3,4,5],[7,8,9,10,11]])
    c = cf([[1,7]])
    d = cf([[1,3,7,8,9]])
    e = cf([[9,10]])
    G = PermGroup([a,b])
    norm = symmetric_normaliser(G, [tracker])
    print(tracker)

if __name__ == '__main__':
    norm_example_1()