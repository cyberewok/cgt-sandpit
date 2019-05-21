if __name__ == '__main__':
    import _example_path_tools


from permutation import Permutation
from permutation_C import Permutation as Perm_C
from schreier_sims import SchreierSimsGenerator
from schreier_sims_legacy import schreier_sims_algorithm, group_size

size = 40
    
def A50_gens(cf):
    a = cf([[1,2,3]])
    b = cf([list(range(2, size + 1))])
    return [a,b]


def schrieier_sims_original(gens, identity):
    base, strong_gens, chain_generators, graphs = schreier_sims_algorithm(gens, identity)
    return group_size(graphs)

def schrieier_sims_new(gens):
    ssg = SchreierSimsGenerator(gens)
    ret = ssg.complete()
    return ret.order()

def schrieier_sims_C(gens):
    ssg = SchreierSimsGenerator(gens)
    ret = ssg.complete()
    return ret.order()
    
if __name__ == '__main__':
    cf = lambda x: Permutation.read_cycle_form(x, size)     
    cf_C = lambda x: Perm_C.read_cycle_form(x, size)     
    
    print(schrieier_sims_original(A50_gens(cf), cf([])))
    print(schrieier_sims_new(A50_gens(cf)))
    import schreier_structure as ss
    ss.Permutation = Perm_C
    
    print(schrieier_sims_C(A50_gens(cf_C)))