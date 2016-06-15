from permutation import Permutation
import schreier_sims as schreier_sims_tools

class PermGroup():
    def __init__(self, generators):
        self.generators = generators        
        if len(generators) > 0:
            g = self.generators[0]
            self.identity = g**-1 * g
        else:
            self.identity = Permutation([1])
        b, strong_gens, chain_gens, sgs = schreier_sims_tools.schreier_sims_algorithm(self.generators, self.identity)
        self.base = b
        self.strong_generators = strong_gens
        self.chain_generators = chain_gens
        self.schreier_graphs = sgs
        self.size = None
        self.elements = None
    
    #len has to return an int so this will not work for large groups unfortunately.
    def __len__(self):
        if self.size is None:
            total = 1
            for num_cosets in [len([g for g in sg if g is not None]) for sg in self.schreier_graphs]:
                total *= num_cosets
            self.size = total
        return self.size
    
    def order(self):
        if self.size is None:
            total = 1
            for num_cosets in [len([g for g in sg if g is not None]) for sg in self.schreier_graphs]:
                total *= num_cosets
            self.size = total
        return self.size
        
    def __contains__(self, key):
        return self.identity == schreier_sims_tools.membership_siftee(key, self.schreier_graphs, self.base, self.identity)
    
    def __str__(self):
        ret = "PermGroup object:\n"
        
        ret += "  All {} generator(s) for the group:\n".format(len(self.generators))            
        for g in self.generators:
            ret += "    {}\n".format(str(g)[1:-1])
            
        ret += "  Base for the group:\n    {}\n".format(self.base)            
               
        if self.elements is not None and len(self.elements) < 1000:
            ret += "  All {} element(s) of the group:\n".format(len(self.elements))
            for g in self.elements:
                ret += "    {}\n".format(str(g)[1:-1])
        
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
    
    def _list_elements(self, key = None):
        if self.elements is not None:
            return self.elements
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
        self.elements = elements_found
        return self.elements    

    def _print_elements(self):
        ele = self._list_elements()
        for g in ele:
            print(str(g)[1:-1])
    
    def _rand_element(self):
        pass

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
        elements = self.group._list_elements(key)
        return [self.left_rep * g * self.right_rep for g in elements]

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