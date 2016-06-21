if __name__ == '__main__':
    import sys
    abs_path = "C:\\Users\\admin-u5887726\\Google Drive\\Phd\\Programming\\cgt-sandpit\\Prototype\\Python\\Playground\\Mark1"
    sys.path.append(abs_path)

from partition import Partition
from permutation import Permutation
from group import PermGroup as Group
from coset_property import CosetProperty as Prop
from coset_property import permutation_commuter
import sims_search



cf =Permutation.read_cycle_form
a = cf([[1, 2]],4)
check = permutation_commuter(a)
b = cf([[1,2,3,4]], 4)
c = cf([[3, 4]], 4)
d = cf([[2, 3]], 4)
e = cf([[3, 4]], 4)
G = Group([a,b])
p = Prop([check])
sims_search.backtrack_subgroup(G, p, None)
