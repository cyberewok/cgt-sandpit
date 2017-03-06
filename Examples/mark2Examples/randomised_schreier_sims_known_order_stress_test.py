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
    
def randomised_known_order(gens):
    tot = 1
    for i in range(3, size+ 1):
        tot*=i
    rg = RandomSchreierGenerator(gens, group_order = tot)
    rg.complete(trials = 20)
    ss = rg.structure
    print(sum(len(chain_gens) for chain_gens in ss.chain_generators))
    print(tot)
    print(ss.order())
    
if __name__ == '__main__':
    randomised_known_order(A50_gens())