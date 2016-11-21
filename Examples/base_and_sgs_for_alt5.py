if __name__ == '__main__':
    from _example_path_tools import add_path_examples
    add_path_examples()
    
from permutation import Permutation
from group import PermGroup
from schreier_sims import _coset_rep_inverse as rep

cf = lambda x: Permutation.read_cycle_form(x,5)
a = cf([[2,3,4]])
b = cf([[1,2,3,4,5]])
A5 = PermGroup.fixed_base_group([a,b],[1,2,3])
print(A5.base)
print(A5.strong_generators)
for sg in A5.schreier_graphs:
    for image in range(1, 6):
        print("{}: {}".format(image, rep(image, sg, A5.identity)))