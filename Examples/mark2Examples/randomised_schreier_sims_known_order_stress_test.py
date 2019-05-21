if __name__ == '__main__':
    import _example_path_tools

from permutation_P import Permutation as P_Permutation
from permutation import Permutation as C_Permutation
from group import PermGroup
from schreier_sims_randomised import RandomSchreierGenerator

size = 200   
    
def A50_gens(cf):
    a = cf([[1,2,3]])
    b = cf([list(range(2, size + 1))])
    return [a,b]
    
def randomised_known_order_P(gens):
    tot = 1
    for i in range(3, size+ 1):
        tot*=i
    rg = RandomSchreierGenerator(gens, group_order = tot)
    rg.complete(trials = 20)
    ss = rg.structure
    print(sum(len(chain_gens) for chain_gens in ss.chain_generators))
    print(tot)
    print(ss.order())

def randomised_known_order_C(gens):
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
    
    cf_C = lambda x: C_Permutation.read_cycle_form(x, size)
    randomised_known_order_C(A50_gens(cf_C))

    cf = lambda x: P_Permutation.read_cycle_form(x, size)
    import schreier_sims_randomised as ssr
    ssr.Permutation = P_Permutation
    import schreier_structure as ss
    ss.Permutation = P_Permutation  
    randomised_known_order_P(A50_gens(cf))  