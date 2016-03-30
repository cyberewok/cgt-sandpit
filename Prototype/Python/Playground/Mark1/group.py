from permutation import Permutation
import schreier_sims as schreier_sims_tools

class PermCoset():
    def __init__(self, elements = None, generators = None, right_rep = None, left_rep = None):
        self.elements = None
        if elements is not None:
            self.elements = elements
        self.generators = []            
        if generators is not None:
            self.generators = generators
        self.right_rep = None
        if right_rep is not None:
            self.right_rep = right_rep
        self.left_rep = None
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
        
        if self.generators is not None:
            ret += "  All {} generator(s) for the assiociated group:\n".format(len(self.generators))            
            for g in self.generators:
                ret += "    {}\n".format(str(g)[1:-1])                
                
        if self.elements is not None and len(self.elements) < 1000:
            ret += "  All {} element(s) of the coset:\n".format(len(self.elements))
            for g in self.elements:
                ret += "    {}\n".format(str(g)[1:-1])
        
        return ret

    def __mul__(self, other):
        #this is for right cosets.
        new_elements = None
        if self.elements is not None:
            new_elements = [g*other for g in self.elements]
        new_right_rep = None
        if self.right_rep is not None:
            new_right_rep = self.right_rep*other
        return PermCoset(new_elements, self.generators, new_right_rep, self.left_rep)
    
    def __rmul__(self, other):
        #this is for left cosets.
        new_elements = None
        if self.elements is not None:
            new_elements = [other*g for g in self.elements]
        new_left_rep = None
        if self.left_rep is not None:
            new_left_rep = other * self.left_rep
        return PermCoset(new_elements, self.generators, self.right_rep, new_left_rep)
    
    def _list_elements(self):
        if self.elements is not None:
            return self.elements
        elements_found = set(self.generators)
        frontier = list(self.generators)
        while len(frontier) != 0:
            cur = frontier.pop()
            for g in self.generators:
                cand = cur * g
                if cand not in elements_found:
                    frontier.append(cand)
                    elements_found.add(cand)
        elements_found = sorted(list(elements_found)) 
        adjusted_coset = self.left_rep * PermCoset(elements_found) * self.right_rep
        self.elements = adjusted_coset.elements
        return self.elements

class PermGroup(PermCoset):
    def __init__(self, generators = None):
        if generators is None or len(generators) == 0:
            self.identity = Permutation([])
        else:
            g = generators[0]
            self.identity = g**-1 * g
        super().__init__(None, generators, self.identity, self.identity)
        b, strong_gens, chain_gens, sgs = schreier_sims_tools.schreier_sims_algorithm(generators, self.identity)
        self.base = b
        self.strong_generators = strong_gens
        self.chain_generators = chain_gens
        self.schreier_graphs = sgs
        self.size = None
        
    def __len__(self):
        if self.size is None:
            total = 1
            for num_cosets in [len([g for g in sg if g is not None]) for sg in self.schreier_graphs]:
                total *= num_cosets
            self.size = total
        return self.size
        
    def __contains__(self, key):
        return self.identity == schreier_sims_tools.membership_siftee(key, self.schreier_graphs, self.base, self.identity)
    
    def _left_cosets(self, subgroup):
        H = subgroup
        cosets = [H]
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
        cosets = [H]
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

    def _print_elements(self):
        ele = self._list_elements()
        for g in ele:
            print(str(g)[1:-1])
    
    def _rand_element(self):
        pass