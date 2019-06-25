import random

from .permutation import Permutation
from .ordering import ordering_to_key
from .schreier_sims import get_schreier_structure, BaseChanger

class PermGroup():
    def __init__(self, generators, schreier_structure = None):
        self.generators = generators #needed feild
        g = self.generators[0]        
        self.degree = len(g) #Needed feild
        self.identity = g**-1 * g #Needed feild
        self.schreier_structure = schreier_structure
        
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
        #Currently unsupported. Should work by making a random element generator
        #from elements and using that in a random schreier sims construction.
        return None
        #min_gen_group(elements, base)

    @classmethod
    def fixed_base_group(cls, gens, base = None, order = None):
        if base is None:
            base = []
        structure = get_schreier_structure(gens, base = base, order = order)        
        return cls(gens, schreier_structure = structure)
    
    @classmethod
    def fixed_order_group(cls, gens, order):
        structure = get_schreier_structure(gens, order = order)
        return cls(gens, schreier_structure = structure)

    @classmethod
    def deep_copy(cls, group):
        return cls.fixed_base_group(group.generators)  
    
    def normaliser(self):
        return None
    
    def canonical_form(self):
        return None
    
    def canonical_generators(self):
        new_structure = get_schreier_structure(self.generators, base = list(range(1, self.degree + 1)), order = self.order())
        return list(new_structure.canonical_generators())
    
    def change_base(self, new_base):
        # this is currently crazy inefficient
        bc = BaseChanger(self)
        self.schreier_structure = bc.change_base(new_base)

    def orbits(self, stab_level = 0, key = None, in_order = False):
        return self.schreier_structure.orbits(level = stab_level, key = key, in_order = in_order)
        #orbits = []
        #visited = [None] * self.degree
        #for ele in range(1, self.degree + 1):
            #if visited[ele - 1] is None:
                #orb = self.orbit(ele, stab_level, key = key)
                #orbits.append(orb)
                #for orb_ele in orb:    
                    #visited[orb_ele - 1] = True
        #return orbits

    def orbit(self, num, stab_level = 0, key = None, in_order = False):
        return self.schreier_structure.orbit(num, level = stab_level, key = key, in_order = in_order)
    
    def base_image_member(self, image):
        return self.schreier_structure.element_from_image(image)
    
    def base_prefix_image_member(self, image):
        return self.schreier_structure.element_from_image(image)
    
    def prefix_postfix_image_member(self, pre, post, allow_base_change = False):
        lookup = {ele:index for index, ele in enumerate(pre)}
        image = []
        for ele in self.schreier_structure.base_till_level():
            if ele in lookup:
                image.append(post[lookup[ele]])
            else:
                if len(image) < len(pre):
                    raise NotImplementedError
                    #needs base change or new group.
                else:
                    break
                
        limit = len(image)
        return self.base_prefix_image_member(image) 
    
    
    #len has to return an int so this will not work for large groups unfortunately.
    #order method is more robust for this reason.
    def __len__(self):
        return self.order()

    def __eq__(self, other):
        if self.degree != other.degree:
            return False
        
        if self.order() != other.order():
            return False
            
        gens = self.generators
        
        for gen in gens:
            if gen not in other:
                return False
        
        return True
    
    def order(self):
        return self.schreier_structure.order()
        
    def __contains__(self, key):
        return key in self.schreier_structure
    
    def __str__(self):
        ret = "PermGroup object:\n"
        
        ret += "  All {} generator(s) for the group:\n".format(len(self.generators))            
        for g in self.generators:
            ret += "    {}\n".format(str(g)[1:-1])
            
        ret += "  Base for the group:\n    {}\n".format(self.schreier_structure.base_till_level())            
        
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
    
    def __pow__(self, exp, mod = None):
        #This is inefficient and would be better to carry over the relabled 
        #schreier structure and relable instead of multiply.
        conj_gens = []
        for gen in self.generators:
            cand = exp ** -1 * gen * exp
            conj_gens.append(cand)
        #conj_structure = None
        #if self.schreier_structure is not None:
            #conj_structure = self.schreier_structure ** exp
        #return PermGroup(conj_gens, self.schreier_structure ** exp)
        return PermGroup.fixed_base_group(conj_gens, list(range(1, self.degree)))
    
    def __lt__(self, other):
        if isinstance(other, PermGroup):
            self.change_base(list(range(1, self.degree)))
            other.change_base(list(range(1, self.degree)))
            return self.schreier_structure < other.schreier_structure
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
        index = random.randrange(size)
        ele = self.schreier_structure.element_at_index(index)
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
    
    
class ExpandableGroup(PermGroup):
    def add_generator(perm):
        pass
    
    

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