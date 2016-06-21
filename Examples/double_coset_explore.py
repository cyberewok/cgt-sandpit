if __name__ == '__main__':
    import sys
    abs_path = "C:\\Users\\admin-u5887726\\Google Drive\\Phd\\Programming\\cgt-sandpit\\Prototype\\Python\\Playground\\Mark1"
    sys.path.append(abs_path)

from partition import Partition
from permutation import Permutation
from group import PermGroup as Group
from coset_property import permutation_commuter

cf =Permutation.read_cycle_form
a = cf([[1, 2]],4)
check = permutation_commuter(a)
b = cf([[1,2,3,4]], 4)
c = cf([[3, 4]], 4)
d = cf([[2, 3]], 4)
e = cf([[3, 4]], 4)
G = Group([a,b])   
G1 = Group([c,d])
G2 = Group([e])
identity = cf([],4)
sub = Group([identity])
for g in G._list_elements():
    d = sub * g * sub
    p_flag = check(g)
    d_flag = d.mid_minimal()
    if g != identity and p_flag and d_flag:
        sub = Group([t for t in sub.generators + [g] if t != identity])
    print("{}\nprop: {}\nmin: {} sub: {}\nd: {}\n".format(g, p_flag, d_flag, sub.generators, d._list_elements()))
Dcosets = [(G2*g*G1, g) for g in G._list_elements()]
for d, g in sorted(Dcosets,key = lambda x: x[0]._list_elements()):
    eles = d._list_elements()
    #print("{} ({}) {}:\n{}\n".format(g,len(eles),d.mid_minimal(),eles))

a = cf([[1,2],[3,4]],4)
b = cf([[1,2,3]],4)
print(len(Group([a,b])))