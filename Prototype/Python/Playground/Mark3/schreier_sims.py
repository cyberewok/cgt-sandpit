from permutation import Permutation
from ordering import ordering_to_key
#from schreier_structure import GraphSchreierStructure as SchreierStructure
from schreier_structure import DirectSchreierStructure as SchreierStructure
#from schreier_structure import SchreierStructure

def get_schreier_structure(gens, order = None, base = None, level = None, previous_structure = None):
    return get_schreier_structure_naive(gens, base)

def get_schreier_structure_naive(gens, base = None):
    ssg = SchreierSimsGenerator(gens, base = base)
    ret = ssg.complete()
    return ret

class RandomisedDirectSchreierSimsModifier():
    def __init__(self, generators, base = None, order = None, previous_structure = None):
        if len(generators) == 0:
            raise ValueError("Must define atleast one generator.")
        
        #can not contain repeats check?
        
        if len(generators) > 1:
            for gen in generators:
                if gen.trivial():
                    raise ValueError("Generators can not be trivial.")
        
        if self.previous_structure is None:
            raise ValueError("Need prevously valid structure.")
        
        self.generators = generators
        self.degree = len(generators[0])
        self.base_candidate = base
        if self.base_candidate is None:
            self.base_candidate = []
        self.depth = 0
        self.structure = DirectSchreierStructure(self.degree)
        
        
        
    def complete(self, level):
        #if we have an existing structure modify it accordingly
        #sift random elements from level down until correct size is reached.
        pass
        siftee = self.structure.sift_on_level(cand, level)
        if siftee is None:
            self.structure.base
    
    
    def add_level(self, cand):
        new_base_ele = self.extend_base(cand)
        self.structure.add_level(new_base_ele)
        self.depth += 1
        
    def extend_base(self, non_id):
        index = len(self.structure.base)
        if index < len(self.base_candidate):
            new_element = self.base_candidate[index]
            return new_element
        elif not non_id.trivial():
            first_non_fixed = next(num for num in range(1, len(non_id) + 1) if num**non_id != num)
            return first_non_fixed
        return list(set(list(range(1, self.degree))) - set(self.structure.base))[0]     
    
    
    

class DirectSchreierSimsGenerator():
    def __init__(self, generators, base = None, order = None):
        if len(generators) == 0:
            raise ValueError("Must define atleast one generator.")
        self.generators = generators
        self.degree = len(generators[0])
        self.base_candidate = base
        if self.base_candidate is None:
            self.base_candidate = []
        self.depth = 0
        self.structure = DirectSchreierStructure(self.degree)
    
    def complete(self):
        pass
    
    def add_level(self, cand):
        new_base_ele = self.extend_base(cand)
        self.structure.add_level(new_base_ele)
        self.depth += 1
        
    def extend_base(self, non_id):
        index = len(self.structure.base)
        if index < len(self.base_candidate):
            new_element = self.base_candidate[index]
            return new_element
        elif not non_id.trivial():
            first_non_fixed = next(num for num in range(1, len(non_id) + 1) if num**non_id != num)
            return first_non_fixed
        return list(set(list(range(1, self.degree))) - set(self.structure.base))[0]       
        
        

class NaiveSchreierSimsGenerator():
    def __init__(self, generators, base = None):
        if len(generators) == 0:
            raise ValueError("Must define atleast one generator.")
        self.generators = generators
        self.degree = len(generators[0])
        self.base_candidate = base
        if self.base_candidate is None:
            self.base_candidate = []
        self.depth = 0
        #shouldn't this be a specific type of schreier structure?
        self.structure = SchreierStructure(self.degree)
        
    def complete(self):
        self._drip_feed_level(self.generators, 0)
        return self.structure
    
    def _schreier_generators(self, gens, level):
        ret = []
        unique = set()
        coset_reps = self.structure.transversal(level)
        for rep in (x for x in coset_reps if x is not None):
            for gen in gens:
                cand = self.structure.sift_on_level(rep * gen, level)
                if cand not in unique and not cand.trivial():
                    ret.append(cand)
                    unique.add(cand)
        return ret

    def _drip_feed_level(self, gens, level):
        if self.depth == level:
            self.add_level(gens[0])
        for gen in gens:
            self.structure.extend_level(gen, level, force_update = True)
        schreier_gens = self._schreier_generators(gens, level)
        if len(schreier_gens) > 0:
            self._drip_feed_level(schreier_gens, level + 1)
            
    def add_level(self, cand):
        new_base_ele = self.extend_base(cand)
        self.structure.add_level(new_base_ele)
        self.depth += 1
        
    def extend_base(self, non_id):
        index = len(self.structure.base)
        if index < len(self.base_candidate):
            new_element = self.base_candidate[index]
            return new_element
        elif not non_id.trivial():
            first_non_fixed = next(num for num in range(1, len(non_id) + 1) if num**non_id != num)
            return first_non_fixed
        return list(set(list(range(1, len(non_id)))) - set(self.structure.base))[0]    
    

class SchreierSimsGenerator():
    def __init__(self, generators, base = None):
        if len(generators) == 0:
            raise ValueError("Must define atleast one generator.")
        self.generators = generators
        self.degree = len(generators[0])
        self.base_candidate = base
        self.chain_gens = []
        self.chain_orbits = []
        if self.base_candidate is None:
            self.base_candidate = []
        self.depth = 0
        self.structure = SchreierStructure(self.degree)
        
    def complete(self):
        self._drip_feed_level(self.generators, 0)
        return self.structure
    
    def single_schreier_generators(self, gen, level, added):
        ret = []
        unique = set()
        coset_reps = self.structure.transversal(level)
        for rep in (x for x in coset_reps if x is not None):
            cand = self.structure.sift_on_level(rep * gen, level)
            if cand not in unique and not cand.trivial():
                ret.append(cand)
                unique.add(cand)
        for rep in (x for x in (coset_reps[ele - 1] for ele in added) if x is not None):
            for old_gen in self.structure.level_generators(level):
                cand = self.structure.sift_on_level(rep * old_gen, level)
                if cand not in unique and not cand.trivial():
                    ret.append(cand)
                    unique.add(cand)
        return ret

    def _drip_feed_level(self, gens, level):
        if self.depth == level:
            self.add_level(gens[0])
        for gen in gens:
            cand = self.structure.siftee(gen, level)
            if cand is None or not cand.trivial():
                self.structure.extend_level(cand, level, force_update = True, improve_tree = False)
                orb = self.structure.stabaliser_orbit(level)
                added = orb - self.chain_orbits[level]
                self.chain_orbits[level] = set(orb)
                schreier_gens = self.single_schreier_generators(cand, level, added)
                if len(schreier_gens) > 0:
                    self._drip_feed_level(schreier_gens, level + 1)
            
    def add_level(self, cand):
        self.chain_orbits.append(set())
        new_base_ele = self.extend_base(cand)
        self.structure.add_level(new_base_ele)
        self.depth += 1
        
    def extend_base(self, non_id):
        index = len(self.structure.base)
        if index < len(self.base_candidate):
            new_element = self.base_candidate[index]
            return new_element
        elif not non_id.trivial():
            first_non_fixed = next(num for num in range(1, len(non_id) + 1) if num**non_id != num)
            return first_non_fixed
        return list(set(list(range(1, len(non_id)))) - set(self.structure.base))[0]

class BaseChanger():
    def __init__(self, group):
        self.group = group
        self.structure = group.schreier_structure
        if self.structure is None:
            self.structure = get_schreier_structure(group.generators)
        self.cached_order = self.structure.order()
        self.cur_base = []
        
    #def pop(self, base_size = None):
        #if base_size is None:
            #base_size = len(self.structure.base) - 1
        
    
    def whole_common_prefix(self, a, b):
        for index in range(min(len(a), len(b))):
            if a[index] != b[index]:
                return True
        return False
    
    def change_base(self, new_base):
        
        need_change = False
        act_base = self.structure.base_till_level()
        
        if self.whole_common_prefix(act_base, new_base):
            need_change = True
        
        self.cur_base = new_base
        if need_change:
            self.structure = get_schreier_structure(self.group.generators, base = new_base, order = self.structure.order())
        return self.structure
    
    def orbit(self, ele):
        return self.structure.orbit(ele, level = len(self.cur_base))
        
    def orbits(self, level = None):
        if level is None:
            level = len(self.cur_base)
        return self.structure.orbits(level = level)
    
    def discrete(self):
        cand = 1
        for level in range(min(len(self.cur_base), len(self.structure.base_till_level()))):
            cand *= len(self.structure.stabaliser_orbit(level))
        return cand == self.cached_order
    
    def stabaliser_orbits(self):
        ret = []
        for level in range(min(len(self.cur_base), len(self.structure.base_till_level()))):
            ret.append(self.structure.stabaliser_orbit(level))
        return ret
    
    def element_from_image(self, image):
        return self.structure.element_from_image(image)
    

def membership_index(candidate, schreier_graphs, base, identity, key = None):
    if key is None:
        ordering = base + [x for x in range(1, len(identity) + 1) if x not in base]
        key = ordering_to_key(ordering)

    index = 0
    siftee = candidate
    total = group_size(schreier_graphs)
    
    for num, schreier_graph in zip(base, schreier_graphs):
        image = num**siftee
        des = 0
        orbit_size = 0
        
        for graph_index, group_ele in enumerate(schreier_graph):
            set_ele = graph_index + 1
            if group_ele is not None:
                orbit_size += 1
                if key(set_ele**(candidate)) < key(num**candidate):
                    des += 1
            
        coset_size = total // orbit_size
        index += coset_size * des
        total = total // orbit_size
        
        coset_rep = _coset_rep_inverse(image, schreier_graph, identity)
        if coset_rep is None:
            break
        siftee = siftee * coset_rep

    if siftee != identity:
        return -1
    else:
        return index

def element_at_index(base, schreier_graphs, index, identity, key = None):
    if key is None:
        ordering = base + [x for x in range(1, len(identity) + 1) if x not in base]
        key = ordering_to_key(ordering)
        
    cand = identity
    total = group_size(schreier_graphs)
    for schreier_graph in schreier_graphs:
        image_cands = [((i+1) ** (cand ** -1), i+1) for i, g in enumerate(schreier_graph) if g is not None]
        image_cands.sort(key = lambda  x: key(x[0]))#should be quickselect instead but may be over engeneered?!
        
        num_cands = len(image_cands)
        des = (index * num_cands)//total
        total = total // num_cands
        index = index % total
        coset_rep = _coset_rep_inverse(image_cands[des][1], schreier_graph, identity)
            
        cand = cand * coset_rep
        
    return cand**-1

def base_image_member(base, image, schreier_graphs, identity):
    candidate = identity
    for index, (num, schreier_graph) in enumerate(zip(base, schreier_graphs)):
        coset_rep = _coset_rep_inverse(image[index], schreier_graph, identity)
        if coset_rep is None:
            return None
        else:
            candidate = candidate * coset_rep
            image = [ele**coset_rep for ele in image]
    return candidate**-1