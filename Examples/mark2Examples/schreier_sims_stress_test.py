if __name__ == '__main__':
    import _example_path_tools


from permutation import Permutation
from group import PermGroup
from leon_preset import symmetric_normaliser
from leon_logger import NodeCounter
from schreier_sims import schreier_sims_algorithm, group_size
from schreier_structure import RandomSchreierGenerator

size = 50
cf = lambda x: Permutation.read_cycle_form(x, size)     
    
def A50_gens():
    a = cf([[1,2,3]])
    b = cf([list(range(2, size + 1))])
    return [a,b]

def schrieier_sims(gens):
    base, strong_gens, chain_generators, graphs = schreier_sims_algorithm(gens, cf([]))
    print(len(strong_gens))
    print(group_size(graphs))
    
if __name__ == '__main__':
    schrieier_sims(A50_gens())