if __name__ == '__main__':
    from _example_path_tools import add_path_examples
    add_path_examples()

from partition import Partition
from permutation import Permutation
from group import PermGroup as Group
from coset_property import CosetProperty as Prop
from coset_property import PermutationCommuterProperty
import sims_search
from ordering import ordering_to_key, ordering_to_perm_key

#Set up group generators
cf = Permutation.read_cycle_form
a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)

#Define ordering of base elements
fix = [1,3,5,9,7,11,2,12,4,6,8,10,13]

#Define corresponding key functions on numbers and perms based on base element ordering
key_single = ordering_to_key(fix)
key_perm = ordering_to_perm_key(fix)

#Construct group
G = Group.fixed_base_group([a,b],fix)

#Find all elements in order
#Print the base and stab orbits of G.
print(G.base)
level_orbits = []
for level in range(len(G.base)):
    to_check = sorted(G.orbit(G.base[level],level), key = key_single)
    level_orbits.append(to_check)
    print(to_check)

#Set up the modulo values for a naive traversal.
mods = [len(orbit) for orbit in level_orbits]
def inc(count, resets):#incrementor function for the naive traversal
    sig = len(count) - 1
    while (count[sig] + 1) % resets[sig] == 0:
        count[sig] = 0
        sig -= 1
    count[sig] += 1
    return sig <0, sig

#The orbits change as we traverse cosets so this is to keep track of the changes
cur_orbits = [list(orbit) for orbit in level_orbits]
cur = [0] * len(G.base) 
finished = False
elements1 = []
sig_change = len(G.base) - 1
cur_reps = [G.identity] * len(G.base)

#Populate the list by traversing the tree
while not finished:
    image_prefix = [orbit[cur[index]] for index, orbit in enumerate(cur_orbits[:sig_change + 1])]
    for index in range(sig_change + 1, len(G.base)):
        rep = G.base_prefix_image_member(image_prefix)
        cur_orbits[index] = sorted([ele**rep for ele in level_orbits[index]], key = key_single)
        image_prefix.append(cur_orbits[index][cur[index]])
    image = image_prefix
    elements1.append(G.base_image_member(image))
    finished, sig_change = inc(cur, mods)   


#Do it in a more naive way (no tree traversal).
elements2 = G._list_elements(key = key_perm)

#Check that the results are the same.
print(list(elements1) == list(elements2))

#Now we have silidified our understanding of listing elements lets hack a function
#to create a min gen set. We do this in an inefecient manner but noting the above
#observations could make a very effcient version of this function.
def naive_min_gen(original_group, ordering):
    eles = original_group._list_elements(key = ordering_to_perm_key(ordering))
    cur_gens = [eles[1]]
    cur_G = Group.fixed_base_group(cur_gens, ordering)
    for ele in eles:
        if ele not in cur_G:
            cur_gens.append(ele)
            cur_G = Group.fixed_base_group(cur_gens, ordering)
            if cur_G.order() == G.order():
                break
    return cur_gens

min_gen = naive_min_gen(G, fix)
print(min_gen)