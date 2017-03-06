if __name__ == '__main__':
    from _example_path_tools import add_path_examples
    add_path_examples()

from partition import Partition
from permutation import Permutation
from group import PermGroup as Group
from coset_property import CosetProperty as Prop
from coset_property import permutation_commuter
import sims_search

a = cf([[1,2],[5,6]], 7)
b = cf([[1,2,3,4],[5,6]], 7)
c = cf([[1,2],[6,7]], 7)
d = cf([[1,2,3,4],[6,7]], 7)
e = cf([[1,2,3,4,5,6,7]], 7)
f = cf([[1,2]], 7)
G1 = Group([a,b])
G2 = Group([c,d])
G3 = Group([e,f])
G1_list = list(G1._list_elements())
G2_list = list(G2._list_elements())
best = 0
for rev in G3._list_elements():

#for rev in [G1.identity]:
    rev_func = [x**rev for x in range(1, 8)]    
    key = lambda x:[rev_func[y - 1] for y in (x*(rev**-1))._func]
    G1_list.sort(key = key)
    G2_list.sort(key = key)
    print(G1_list)
    print(G2_list)
    i = 0
    while G1_list[i] == G2_list[i]:
        i+=1
    print("{} {}".format(i, rev_func))
    best = max(i,best)
    if i==0:
        print("ERROR")
        break
print(best)