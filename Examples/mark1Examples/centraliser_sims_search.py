if __name__ == '__main__':
    from _example_path_tools import add_path_examples
    add_path_examples()

from partition import Partition
from permutation import Permutation
from group import PermGroup as Group
from coset_property import CosetProperty as Prop
from coset_property import PermutationCommuterProperty
import sims_search

def _respected_partition(comm):
    comm_group = Group([comm])
    orbs = comm_group.orbits()
    len_orb = dict()
    for orb in orbs:
        if len(orb) in len_orb:
            len_orb[len(orb)].extend(orb)
        else:
            len_orb[len(orb)] = orb
    return Partition(len_orb.values())

def _partition_heuristic(base, image, part):
    for b,i in zip(base,image):
        for cell in part:
            if b in cell: 
                if i in cell:
                    break
                else:
                    return True
    return False

cf =Permutation.read_cycle_form
a = cf([[1, 2]],4)
check = PermutationCommuterProperty(a)
b = cf([[1,2,3,4]], 4)
G = Group([a,b])
p = Prop([check])
cull = lambda base, image: _partition_heuristic(base, image, _respected_partition(a))
print(sims_search.backtrack_subgroup(G, p, cull))