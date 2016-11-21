from permutation import Permutation
import schreier_sims as schreier_sims_tools
import random
from ordering import ordering_to_key

class PermGroup():
    def __init__(self, generators, schreier_sims_info = None):
        self.generators = generators        
        if len(generators) > 0:
            g = self.generators[0]
            self.identity = g**-1 * g
        else:
            self.identity = Permutation([1])
        if schreier_sims_info is None:
            b, strong_gens, chain_gens, sgs = schreier_sims_tools.schreier_sims_algorithm(self.generators, self.identity)
        else:
            b, strong_gens, chain_gens, sgs = schreier_sims_info
        self.base = b
        self.strong_generators = strong_gens
        self.chain_generators = chain_gens
        self.schreier_graphs = sgs
        
    @classmethod
    def min_gen_group(cls, gens, ordering = None):
        size = len(gens[0])
        if ordering is None or len(ordering) < size:
            ordering = list(range(1,size + 1))
        G = Group.fixed_base_group(gens, ordering)
        eles = G._list_elements(key = ordering_to_key(ordering))
        cur_gens = [eles[1]]
        cur_G = Group.fixed_base_group(cur_gens, ordering)
        for ele in eles:
            if ele not in cur_G:
                cur_gens.append(ele)
                cur_G = Group.fixed_base_group(cur_gens, ordering)
                if cur_G.order() == G.order():
                    break
        return cls(cur_gens)
    
    @classmethod
    def all_elements_group(cls, elements, base = None):
        min_gen_group(elements, base)

    @classmethod
    def fixed_base_group(cls, gens, base):
        if len(gens) > 0:
            g = gens[0]
            e = g**-1 * g
        else:
            e = Permutation([1])        
        return cls(gens, schreier_sims_info = schreier_sims_tools.schreier_sims_algorithm_fixed_base(gens, base, e))
    
    def change_base(self, new_base):
        prefix_size = min(len(self.base), len(new_base))
        if self.base[:prefix_size] != new_base[:prefix_size]:
            #the bases diverge at some (possibly redundant) point.
            #in the future this should be smarter and check for redundant elements
            #too but on the other hand that can also be taken care of in a
            #future version of schreier_sims_tools (i.e. provide support for base change)
            ss_info = schreier_sims_tools.schreier_sims_algorithm_fixed_base(self.generators, new_base, self.identity)
            self.base = ss_info[0]
            self.strong_generators = ss_info[1]
            self.chain_generators = ss_info[2]
            self.schreier_graphs = ss_info[3]        

    def orbits(self, stab_level = 0, key = None):
        orbits = []
        visited = set()
        for ele in range(1, len(self.identity) + 1):
            if ele not in visited:
                orb = self.orbit(ele, stab_level, key = key)
                orbits.append(orb)
                visited.update(orb)
        return orbits

    def orbit(self, num, stab_level = 0, key = None):
        if stab_level >= len(self.base):
            return [num]
        if self.schreier_graphs[stab_level][num - 1] is not None:
            orb = self._orbit_schreier(stab_level)
        else:
            orb = self._orbit_computation(num, stab_level)
        return sorted(orb, key = key)    
    
    def _orbit_schreier(self, stab_level):
        return [index + 1 for index, ele in enumerate(self.schreier_graphs[stab_level]) if ele is not None]
    
    def _orbit_computation(self, num, stab_level):
        gens = self.chain_generators[stab_level]
        frontier = [num]
        orb = set(frontier)
        while len(frontier) > 0:
            next_frontier = []
            for gen in gens:
                for num in frontier:
                    cand = num**gen
                    if cand not in orb:
                        orb.add(cand)
                        next_frontier.append(cand)
            frontier = next_frontier
        return list(orb)
    
    def base_image_member(self, image):
        return schreier_sims_tools.base_image_member(self.base, image, self.schreier_graphs, self.identity)
    
    def base_prefix_image_member(self, image):
        limit = len(image)
        return schreier_sims_tools.base_image_member(self.base[:limit], image, self.schreier_graphs[:limit], self.identity)
    
    def prefix_postfix_image_member(self, pre, post, allow_base_change = False):
        lookup = {ele:index for index, ele in enumerate(pre)}
        image = []
        for ele in self.base:
            if ele in lookup:
                image.append(post[lookup[ele]])
            else:
                if len(image) < len(pre):
                    raise NotImplementedError
                    #needs base change or new group.
                else:
                    break
                
        limit = len(image)
        return schreier_sims_tools.base_image_member(self.base[:limit], image, self.schreier_graphs[:limit], self.identity)    
    
    #len has to return an int so this will not work for large groups unfortunately.
    def __len__(self):
        return self.order()
    
    def order(self):
        return schreier_sims_tools.group_size(self.schreier_graphs)
        
    def __contains__(self, key):
        return self.identity == schreier_sims_tools.membership_siftee(key, self.schreier_graphs, self.base, self.identity)
    
    def __str__(self):
        ret = "PermGroup object:\n"
        
        ret += "  All {} generator(s) for the group:\n".format(len(self.generators))            
        for g in self.generators:
            ret += "    {}\n".format(str(g)[1:-1])
            
        ret += "  Base for the group:\n    {}\n".format(self.base)            
        
        return ret

    def __mul__(self, other):
        #this is for right cosets.
        if isinstance(other, Permutation):
            return PermCoset(self, other, None)
        else:
            return NotImplemented
    
    def __rmul__(self, other):
        #this is for left cosets.
        if isinstance(other, Permutation):
            return PermCoset(self, None, other)
        else:
            return NotImplemented
    
    #def _yield_elements(self):
        ##Find all elements in order
        #level_orbits = []
        #for level in range(len(self.base)):
            #to_check = sorted(self.orbit(self.base[level],level), key = key_single)
            #level_orbits.append(to_check)
            #print(to_check)
        
        ##Set up the modulo values for a naive traversal.
        #mods = [len(orbit) for orbit in level_orbits]
        #def inc(count, resets):#incrementor function for the naive traversal
            #sig = len(count) - 1
            #while (count[sig] + 1) % resets[sig] == 0:
                #count[sig] = 0
                #sig -= 1
            #count[sig] += 1
            #return sig <0, sig
        
        ##The orbits change as we traverse cosets so this is to keep track of the changes
        #cur_orbits = [list(orbit) for orbit in level_orbits]
        #cur = [0] * len(G.base) 
        #finished = False
        #elements1 = []
        #sig_change = len(G.base) - 1
        #cur_reps = [G.identity] * len(G.base)
        
        ##Populate the list by traversing the tree
        #while not finished:
            #image_prefix = [orbit[cur[index]] for index, orbit in enumerate(cur_orbits[:sig_change + 1])]
            #for index in range(sig_change + 1, len(G.base)):
                #rep = G.base_prefix_image_member(image_prefix)
                #cur_orbits[index] = sorted([ele**rep for ele in level_orbits[index]], key = key_single)
                #image_prefix.append(cur_orbits[index][cur[index]])
            #image = image_prefix
            #elements1.append(G.base_image_member(image))
            #finished, sig_change = inc(cur, mods)          
    
    def _list_elements(self, key = None):
#        if self.elements is not None:
#            return self.elements
        elements_found = set(self.generators + [self.identity])
        frontier = list(self.generators)
        while len(frontier) != 0:
            cur = frontier.pop()
            for g in self.generators:
                cand = cur * g
                if cand not in elements_found:
                    frontier.append(cand)
                    elements_found.add(cand)
        elements_found = tuple(sorted(list(elements_found), key = key)) 
        #self.elements = elements_found
        return elements_found    

    def _print_elements(self):
        ele = self._list_elements()
        for g in ele:
            print(str(g)[1:-1])
    
    def _rand_element(self):
        size = self.order()
        index = random.choice(range(size))
        ele = schreier_sims_tools.element_at_index(self.base, self.schreier_graphs, index, self.identity)
        return ele
            
            

    def _left_cosets(self, subgroup):
        H = subgroup
        cosets = [H*self.identity]
        coset_leaders = [self.identity]
        frontier = [self.identity]
        while len(frontier) != 0:
            cur = frontier.pop()
            for g in self.generators:
                new_coset = True
                cand = g * cur
                for h in coset_leaders:
                    if cand * (h ** -1) in H:
                        new_coset = False
                        break
                if new_coset:
                    cosets.append(cand*H)
                    coset_leaders.append(cand)
                    frontier.append(cand)                    
        return cosets 
    
    def _right_cosets(self, subgroup):
        H = subgroup
        cosets = [H*self.identity]
        coset_leaders = [self.identity]
        frontier = [self.identity]
        while len(frontier) != 0:
            cur = frontier.pop()
            for g in self.generators:
                new_coset = True
                cand = cur * g
                for h in coset_leaders:
                    if cand * (h ** -1) in H:
                        new_coset = False
                        break
                if new_coset:
                    cosets.append(H * cand)
                    coset_leaders.append(cand)
                    frontier.append(cand)
        return cosets
    

class PermCoset():
    def __init__(self, group, right_rep = None, left_rep = None):
        self.group = group
        self.right_rep = group.identity
        if right_rep is not None:
            self.right_rep = right_rep
        self.left_rep = group.identity
        if left_rep is not None:
            self.left_rep = left_rep
    
    def __str__(self):
        ret = "PermCoset object:\n"
        if self.left_rep is not None and len(self.left_rep.cycle_notation()) != 0:
            ret += "  Left coset representative:\n"
            ret += "    {}\n".format(str(self.left_rep)[1:-1])
            
        if self.right_rep is not None and len(self.right_rep.cycle_notation()) != 0:
            ret += "  Right coset representative:\n"
            ret += "    {}\n".format(str(self.right_rep)[1:-1])
        
        ret += "  Assiociated group:----------\n{}-----------\n".format(self.group)
        
        return ret

    def __mul__(self, other):
        #this is for right cosets.
        if isinstance(other, Permutation):
            new_right_rep = self.right_rep*other 
            return PermCoset(group, new_right_rep, self.left_rep)
        elif isinstance(other, PermGroup):
            return PermDoubleCoset(self.group, self.right_rep, other)
        else:
            return NotImplemented
    
    def __rmul__(self, other):
        #this is for left cosets.
        if isinstance(other, Permutation):
            new_left_rep = self.left_rep*other 
            return PermCoset(group, self.right_rep, new_left_rep)
        else:
            return NotImplemented
        
    
    def _list_elements(self, key = None):
        elements = self.group._list_elements()
        return sorted([self.left_rep * g * self.right_rep for g in elements], key = key)

class PermDoubleCoset():
    def __init__(self, left_group, mid_rep, right_group):
        self.left_group = left_group 
        self.mid_rep = mid_rep
        self.right_group = right_group
        self.min_rep = None
        
    def __str__(self):
        ret = "PermDoubleCoset object:\n"
        
        ret += "  Assiociated left group:----------\n{}-----------\n".format(self.left_group)
        ret += "  Mid element: {}\n".format(self.mid_rep)        
        ret += "  Assiociated right group:----------\n{}-----------\n".format(self.right_group)
        
        return ret
    
    def minimal_rep(self, key = None, key_change = False):
        if self.min_rep is None or key_change:
            self.min_rep = self._list_elements(key = key)[0]
        return self.min_rep
        
    def mid_minimal(self, key = None):
        return self.minimal_rep(key = key) == self.mid_rep
    
    def _list_elements(self, key = None):
        ele1 = self.left_group._list_elements()
        ele2 = self.right_group._list_elements()
        mid = self.mid_rep
        ret = set()
        for l in ele1:
            for r in ele2:
                ret.add(l*mid*r)
        return sorted(list(ret), key =key)