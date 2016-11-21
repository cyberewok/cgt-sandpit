from group import PermGroup
from permutation import Permutation

_base_size = 6
cf = lambda x : Permutation.read_cycle_form(x, _base_size)
a= cf([[1,2,3,4]])
b= cf([[1,2]])
c= cf([[1,2,3]])
s4 = PermGroup([a,b])
s3 = PermGroup([b,c])
for coset in s4._right_cosets(s3):
    print(coset._list_elements())
for coset in s4._left_cosets(s3):
    print(coset._list_elements())    

cf  = Permutation.read_cycle_form
a = cf([[1, 2, 3,4,5]],5)
b = cf([[1,2,3]], 5)
G=PermGroup([a,b])
print(len(G))


