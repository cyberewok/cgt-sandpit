if __name__ == '__main__':
    import _example_path_tools


from permutation import Permutation
from group import PermGroup
from leon_preset import symmetric_normaliser
from leon_logger import NodeCounter
from schreier_sims import schreier_sims_algorithm, group_size
from schreier_sims_randomised import RandomSchreierGenerator
from random_element_generator import UniformGenerator

size = 200
cf = lambda x: Permutation.read_cycle_form(x, size)     
    
def A50_gens():
    a = cf([[1,2,3]])
    b = cf([list(range(2, size + 1))])
    return [a,b]

def randomised_schreier_sims(gens):
    rg = RandomSchreierGenerator(gens)
    rg.complete(trials = 5)
    ss = rg.structure
    print(sum(len(chain_gens) for chain_gens in ss.chain_generators))
    #print(ss.order())
    
if __name__ == '__main__':
    randomised_schreier_sims(A50_gens())