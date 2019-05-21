from permutation import Permutation
from ordering import ordering_to_key
from math import log2

class SchreierStructure():
    def __init__(self, degree):
        self.degree = degree
        self.identity = Permutation.read_cycle_form([], degree)
        self.chain_generators = []
        self.schreier_reps = []
        self.schreier_graphs = []
        #base is needed as a feild.
        self.base = []
        self.stabaliser_orbits = []
    
    def base_at_level(self, level):
        return self.base[level]
    
    def base_till_level(self, level = None):
        if level is None:
            level = len(self.base) 
        return self.base[:level]
        
    def level_generators(self, level):
        return self.chain_generators[level]
    
    def stabaliser_orbit(self, level = 0):
        return self.stabaliser_orbits[level]
    
    def add_to_stabaliser_orbit(self, elements, level = 0):
        self.stabaliser_orbits[level].update(elements)
    
    def _extend_level_single(self, g, level, frontier = None, force_update = False, improve_tree = True):
        #optimisation idea sort the frontier by cost
        updated = False
        graph = self.schreier_graphs[level]
        if frontier is None:
            frontier = self.stabaliser_orbit(level)
        
        new_frontier = []
        visited = [False] * (self.degree + 1)
        updates = []
        for cand in frontier:
            if not visited[cand]:
                cand_cycle = g.element_cycle(cand)
                cycle_size = len(cand_cycle)
                for power, ele in enumerate(cand_cycle):
                    index = ele - 1
                    inverse, _, cost = graph[index]
                    inverse_power = cycle_size - power
                    new_cost = graph[cand - 1][2] + 1
                    if inverse is None:
                        updated = True
                        updates.append((index, (g, inverse_power, new_cost)))
                        new_frontier.append(ele)
                    else:
                        if improve_tree and new_cost < cost:
                            updates.append((index, (g, inverse_power, new_cost)))
                    visited[ele] = True                
                            
        
        #Apply found updates if there is a new element in the orbit
        if updated or force_update:
            for index, node in updates:
                graph[index] = node        
        
        return updated, new_frontier
     
    def extend_level(self, g, level, force_update = False, improve_tree = True):
        #optimisation idea sort the frontier by cost
        frontier = self.stabaliser_orbit(level)
        updated, frontier = self._extend_level_single(g, level, frontier, force_update, improve_tree)
         
        if updated:
            self.add_to_stabaliser_orbit(frontier, level)  
            self.chain_generators[level].append(g)
            additions = [0] * (len(self.chain_generators[level]) - 1) + [len(frontier)]
    
            gen_index = 0
            frontier_index = additions[gen_index]      
            
            while frontier_index < len(frontier):
                #get the current generator
                gen = self.chain_generators[level][gen_index]
                
                #try update the frontier with it (only using unseen points).
                _, new_frontier = self._extend_level_single(gen, level, frontier[frontier_index:], True)
                
                #keep track of how many new points reached
                additions[gen_index] = len(new_frontier)
                
                #update the frontier
                self.add_to_stabaliser_orbit(new_frontier, level)            
                if len(new_frontier) > 0:
                    frontier.extend(new_frontier)
                
                #update the index and the pointer to the new part of frontier.
                gen_index = (gen_index + 1) % len(self.chain_generators[level])
                frontier_index += additions[gen_index]
        elif force_update:
            self.chain_generators[level].append(g)            

        return updated
        
    def add_level(self, base_element):
        self.chain_generators.append([])
        graph = [(None, 1, 0) for _ in range(self.degree)]
        index = base_element - 1
        graph[index] = (self.identity, 1, 0)
        self.schreier_graphs.append(graph)
        self.base.append(base_element)
        self.stabaliser_orbits.append(set([base_element]))
    
    def sift_on_level(self, g, level):
        if level < 0:
            #This indicates we want to sift before stabalising anything.
            return g
        cand = self.base[level] ** g
        inverse = self.stabaliser_representative(cand, level)
        if inverse is None:
            return None
        return g * inverse
    
    def siftee(self, g, level = 0):
        for cur_level in range(level, len(self.base)):
            cand = self.sift_on_level(g, cur_level)
            if cand is None:
                return g
            elif cand.trivial():
                return cand
            g = cand
        return g
    
    def membership(self, g, level = 0):
        cand = self.siftee(g, level)
        return (cand is not None) and cand.trivial()
    
    def __contains__(self, g):
        return self.membership(g)
    
    def __lt__(self, other):
        if isinstance(other, type(self)):
            for self_gen, other_gen in zip(self.canonical_generators(), other.canonical_generators()):
                if self_gen != other_gen:
                    if self_gen < other_gen:
                        return True
                    else:
                        return False
            return False
                        
            
            ##compare base?
            #if self.base != other.base:
                #return self.base < other.base
            
            ##compare orbit sizes/elements
            #for level in range(len(self.base)):
                #self_orb = self.stabaliser_orbit[level]
                #other_orb = other.stabaliser_orbit[level]
                
                #self_min = None                
                #for ele in self_orb:
                    #if ele not in other_orb:
                        #if self_min is None or ele < self_min:
                            #self_min = ele
                
                #other_min = None                
                #for ele in other_orb:
                    #if ele not in self_orb:
                        #if other_min is None or ele < other_min:
                            #other_min = ele
                
                #if self_min is not None and other_min is not None:
                    #return self_min < other_min
                
                #if self_min is not None:
                    #return True
                
                #if other_min is not None:
                    #return False
            
                
            ##compare leftmost branch right most children
        else:
            return NotImplemented
            
    def canonical_generators(self):
        for level in reversed(range(len(self.base))):
            #calc the representative for each image (the fast way).
            #use this to initialise cand
            #should possibly store this sorted.
            madan = True
            for rep in self.transversal(level):
                if rep is not None:
                    if madan:
                        madan = False
                    else:
                        yield self.leftmost_child(rep, level + 1)
    
    def leftmost_child(self, coset_rep, level):
        # 1: if bottom level return cand
        # 2: look at orbits from one level down when acted on by cand
        # 3: take the smallest image and the rep for that image and make cand = rep * cand
        # 4: go1
        cand = coset_rep
        for cur_level in range(level, len(self.base)):
            best_image = None
            best_pre = None
            for pre in self.stabaliser_orbit(cur_level):
                cand_image = pre ** cand
                if best_image is None or cand_image < best_image:
                    best_image = cand_image
                    best_pre = pre
            rep = self.stabaliser_representative(best_pre, cur_level)
            cand = (rep ** -1) * cand
        return cand
    
    def stabaliser_representative(self, image, level):
        """Returns the coset representative inverse for coset associated with 
        the image reachable in the schreier_graph."""
        graph = self.schreier_graphs[level]
        g = self.identity
        cur_index = image - 1
        cur_num = image
        cur_g_base, cur_pow, _ = graph[cur_index]
        if cur_g_base is None:
            return None
        while cur_num != self.base[level]:# and cur_g_base is not None:# and cur_pow > 0:
            cur_g = cur_g_base ** cur_pow
            #Follow the chain to the identity and multiply by the schreier graph element.
            g = g * cur_g
            image = cur_num ** cur_g
            cur_index = image - 1
            cur_num = image
            cur_g_base, cur_pow, _ = graph[cur_index]
        return g

    
    def transversal(self, level):
        #this is the inefficient version.
        #you should store temp paths to do efficiently (as you are stroing them anyway)
        #invs = [self.stabaliser_representative(image, level) for image in range(self.degree, 0, -1)]
        #ret = []
        #for g in reversed(invs):
            #if g is not None:
                #ret.append(g ** -1)
            #else:
                #ret.append(None)
        #return ret
        #better way:
        ret = [None] * self.degree
        for index, g in enumerate(self.transversal_inverses(level)):
            if g is not None:
                ret[index] = g ** -1
        return ret
        
    def transversal_inverses(self, level):
        #initialise ret
        #for each possible value in degree check if graph is None
        #if not follow path back till get to a non none
        ret = [None] * self.degree
        ret[self.base[level] - 1] = self.identity
        graph = self.schreier_graphs[level]
        for image in range(1, self.degree + 1):
            cur_index = image - 1
            cur_num = image
            g_chain = []            
            cur_g_base, cur_pow, _ = graph[cur_index]
            if cur_g_base is not None:    
                while ret[cur_index] is None:
                    cur_g = cur_g_base ** cur_pow
                    g_chain.append((cur_index, cur_g))
                    image = cur_num ** cur_g
                    cur_index = image - 1
                    cur_num = image
                    cur_g_base, cur_pow, _ = graph[cur_index]
                rest = ret[cur_index]
                for chain_index, chain_g in reversed(g_chain):
                    rest = chain_g * rest
                    ret[chain_index] = rest   
        return ret
    
    
    def discrete(self):
        #This is not true. Need better condition.
        if len(self.stabaliser_orbits[-1]) == 0:
            return False
        return len(self.stabaliser_orbits[-1]) == 1
    
    def order(self):
        tot = 1
        for orb in self.stabaliser_orbits:
            tot *= len(orb)
        return tot
    
    def orbits(self, level = 0, key = None, in_order = False):
        orbits = []
        visited = [None] * self.degree
        for ele in range(1, self.degree + 1):
            if visited[ele - 1] is None:
                orb = self.orbit(ele, level, key = key)
                orbits.append(orb)
                for orb_ele in orb:    
                    visited[orb_ele - 1] = True
        return orbits
        
    
    def orbit(self, num, level = 0, key = None, in_order = False):
        if level >= len(self.base):
            return [num]
        orb = self._orbit_computation(num, level)
        if in_order:
            ret = sorted(orb, key = key)
        else:
            ret = orb
        return ret
      
    def _orbit_computation(self, num, level):
        # there are better ways to do this. BUt is it too step a price to avoid the hash check.
        gens = self.level_generators(level)
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
    
    def membership_index(self, g, key = None):
        if key is None:
            ordering = self.base + [x for x in range(1, self.degree + 1) if x not in self.base]
            key = ordering_to_key(ordering)
        #divide current order by len of orbit
        #add index used * current order to ret
        
        cand = g
        #sift on level keeping track of which index out of tot
        ret = 0
        cur_order = self.order()
        go_leftmost = False
        
        for cur_level in range(0, len(self.base)):
            cur_orbit = self.stabaliser_orbit(cur_level)
            cur_order //= len(cur_orbit)
            
            image = self.base[cur_level] ** cand
            post_image = self.base[cur_level] ** g
            found = False
            des_index = 0
            for end in cur_orbit:
                if key(end ** g) < key(post_image):
                    des_index += 1
            
            ret += des_index * cur_order            
            
            if image not in cur_orbit:
                break
            
            if not cand.trivial():
                cand = self.sift_on_level(cand, cur_level)
        
        return ret
    
    def element_at_index(self, index, key = None):
        if index < 0 or index >= self.order():
            return None
        if key is None:
            ordering = self.base + [x for x in range(1, self.degree + 1) if x not in self.base]
            key = ordering_to_key(ordering)
        
        ret = self.identity
        
        cur_order = self.order()
        for cur_level in range(0, len(self.base)):
            cur_orbit = self.stabaliser_orbit(cur_level)
            cur_order //= len(cur_orbit)
            des_index = index // cur_order
            index -= des_index * cur_order
            
            #this should be a quick select algorithm if hi performance required.
            image = sorted([(ele ** ret, ele) for ele in cur_orbit], key = lambda x:key(x[0]))[des_index][1]
            inverse = self.stabaliser_representative(image, cur_level)
            if inverse is None:
                raise ValueError("Unexpected orbit violation.")
            ret = (inverse ** (-1)) * ret  
        
        return ret
        
    def element_from_image(self, image):      
        ret = self.identity
        for cur_level in range(0, len(self.base)):
            
            #this should be a quick select algorithm if hi performance required
            des_image = self.base_at_level(cur_level)
            if cur_level < len(image):
                cur_orbit = self.stabaliser_orbit(cur_level)                
                des_image = image[cur_level] ** ret
                if des_image not in cur_orbit:
                    return None
            inverse = self.stabaliser_representative(des_image, cur_level)
            ret = ret * inverse  
        
        return ret ** -1
    
class VectorSchreierStructure(SchreierStructure):
    def __init__(self, degree):
        self.degree = degree
        self.identity = Permutation.read_cycle_form([], degree)
        self.chain_generators = []
        self.schreier_graphs = []
        #base is needed as a feild.
        self.base = []
        self.stabaliser_orbits = []
    
    def base_at_level(self, level):
        return self.base[level]
    
    def base_till_level(self, level = None):
        if level is None:
            level = len(self.base) 
        return self.base[:level]
        
    def level_generators(self, level):
        return self.chain_generators[level]
    
    def stabaliser_orbit(self, level = 0):
        return self.stabaliser_orbits[level]
    
    def add_to_stabaliser_orbit(self, elements, level = 0):
        self.stabaliser_orbits[level].update(elements)
    
    def _extend_level_single(self, g, level, frontier = None, force_update = False, improve_tree = True):
        #optimisation idea sort the frontier by cost
        updated = False
        graph = self.schreier_graphs[level]
        if frontier is None:
            frontier = self.stabaliser_orbit(level)
        
        new_frontier = []
        visited = [False] * (self.degree + 1)
        updates = []
        for cand in frontier:
            if not visited[cand]:
                cand_cycle = g.element_cycle(cand)
                cycle_size = len(cand_cycle)
                for power, ele in enumerate(cand_cycle):
                    index = ele - 1
                    inverse, _, cost = graph[index]
                    inverse_power = cycle_size - power
                    new_cost = graph[cand - 1][2] + 1
                    if inverse is None:
                        updated = True
                        updates.append((index, (g, inverse_power, new_cost)))
                        new_frontier.append(ele)
                    else:
                        if improve_tree and new_cost < cost:
                            updates.append((index, (g, inverse_power, new_cost)))
                    visited[ele] = True                
                            
        
        #Apply found updates if there is a new element in the orbit
        if updated or force_update:
            for index, node in updates:
                graph[index] = node        
        
        return updated, new_frontier
     
    def extend_level(self, g, level, force_update = False, improve_tree = True):
        #optimisation idea sort the frontier by cost
        frontier = self.stabaliser_orbit(level)
        updated, frontier = self._extend_level_single(g, level, frontier, force_update, improve_tree)
         
        if updated:
            self.add_to_stabaliser_orbit(frontier, level)  
            self.chain_generators[level].append(g)
            additions = [0] * (len(self.chain_generators[level]) - 1) + [len(frontier)]
    
            gen_index = 0
            frontier_index = additions[gen_index]      
            
            while frontier_index < len(frontier):
                #get the current generator
                gen = self.chain_generators[level][gen_index]
                
                #try update the frontier with it (only using unseen points).
                _, new_frontier = self._extend_level_single(gen, level, frontier[frontier_index:], True)
                
                #keep track of how many new points reached
                additions[gen_index] = len(new_frontier)
                
                #update the frontier
                self.add_to_stabaliser_orbit(new_frontier, level)            
                if len(new_frontier) > 0:
                    frontier.extend(new_frontier)
                
                #update the index and the pointer to the new part of frontier.
                gen_index = (gen_index + 1) % len(self.chain_generators[level])
                frontier_index += additions[gen_index]
        elif force_update:
            self.chain_generators[level].append(g)            

        return updated
        
    def add_level(self, base_element):
        self.chain_generators.append([])
        graph = [(None, 1, 0) for _ in range(self.degree)]
        index = base_element - 1
        graph[index] = (self.identity, 1, 0)
        self.schreier_graphs.append(graph)
        self.base.append(base_element)
        self.stabaliser_orbits.append(set([base_element]))
    
    def sift_on_level(self, g, level):
        if level < 0:
            #This indicates we want to sift before stabalising anything.
            return g
        cand = self.base[level] ** g
        inverse = self.stabaliser_representative(cand, level)
        if inverse is None:
            return None
        return g * inverse
    
    def siftee(self, g, level = 0):
        for cur_level in range(level, len(self.base)):
            cand = self.sift_on_level(g, cur_level)
            if cand is None:
                return g
            elif cand.trivial():
                return cand
            g = cand
        return g
    
    def membership(self, g, level = 0):
        cand = self.siftee(g, level)
        return (cand is not None) and cand.trivial()
    
    def __contains__(self, g):
        return self.membership(g)
    
    def __lt__(self, other):
        if isinstance(other, type(self)):
            for self_gen, other_gen in zip(self.canonical_generators(), other.canonical_generators()):
                if self_gen != other_gen:
                    if self_gen < other_gen:
                        return True
                    else:
                        return False
            return False
                        
            
            ##compare base?
            #if self.base != other.base:
                #return self.base < other.base
            
            ##compare orbit sizes/elements
            #for level in range(len(self.base)):
                #self_orb = self.stabaliser_orbit[level]
                #other_orb = other.stabaliser_orbit[level]
                
                #self_min = None                
                #for ele in self_orb:
                    #if ele not in other_orb:
                        #if self_min is None or ele < self_min:
                            #self_min = ele
                
                #other_min = None                
                #for ele in other_orb:
                    #if ele not in self_orb:
                        #if other_min is None or ele < other_min:
                            #other_min = ele
                
                #if self_min is not None and other_min is not None:
                    #return self_min < other_min
                
                #if self_min is not None:
                    #return True
                
                #if other_min is not None:
                    #return False
            
                
            ##compare leftmost branch right most children
        else:
            return NotImplemented
            
    def canonical_generators(self):
        for level in reversed(range(len(self.base))):
            #calc the representative for each image (the fast way).
            #use this to initialise cand
            #should possibly store this sorted.
            madan = True
            for rep in self.transversal(level):
                if rep is not None:
                    if madan:
                        madan = False
                    else:
                        yield self.leftmost_child(rep, level + 1)
    
    def leftmost_child(self, coset_rep, level):
        # 1: if bottom level return cand
        # 2: look at orbits from one level down when acted on by cand
        # 3: take the smallest image and the rep for that image and make cand = rep * cand
        # 4: go1
        cand = coset_rep
        for cur_level in range(level, len(self.base)):
            best_image = None
            best_pre = None
            for pre in self.stabaliser_orbit(cur_level):
                cand_image = pre ** cand
                if best_image is None or cand_image < best_image:
                    best_image = cand_image
                    best_pre = pre
            rep = self.stabaliser_representative(best_pre, cur_level)
            cand = (rep ** -1) * cand
        return cand
    
    def stabaliser_representative(self, image, level):
        """Returns the coset representative inverse for coset associated with 
        the image reachable in the schreier_graph."""
        graph = self.schreier_graphs[level]
        g = self.identity
        cur_index = image - 1
        cur_num = image
        cur_g_base, cur_pow, _ = graph[cur_index]
        if cur_g_base is None:
            return None
        while cur_num != self.base[level]:# and cur_g_base is not None:# and cur_pow > 0:
            cur_g = cur_g_base ** cur_pow
            #Follow the chain to the identity and multiply by the schreier graph element.
            g = g * cur_g
            image = cur_num ** cur_g
            cur_index = image - 1
            cur_num = image
            cur_g_base, cur_pow, _ = graph[cur_index]
        return g

    
    def transversal(self, level):
        #this is the inefficient version.
        #you should store temp paths to do efficiently (as you are stroing them anyway)
        #invs = [self.stabaliser_representative(image, level) for image in range(self.degree, 0, -1)]
        #ret = []
        #for g in reversed(invs):
            #if g is not None:
                #ret.append(g ** -1)
            #else:
                #ret.append(None)
        #return ret
        #better way:
        ret = [None] * self.degree
        for index, g in enumerate(self.transversal_inverses(level)):
            if g is not None:
                ret[index] = g ** -1
        return ret
        
    def transversal_inverses(self, level):
        #initialise ret
        #for each possible value in degree check if graph is None
        #if not follow path back till get to a non none
        ret = [None] * self.degree
        ret[self.base[level] - 1] = self.identity
        graph = self.schreier_graphs[level]
        for image in range(1, self.degree + 1):
            cur_index = image - 1
            cur_num = image
            g_chain = []            
            cur_g_base, cur_pow, _ = graph[cur_index]
            if cur_g_base is not None:    
                while ret[cur_index] is None:
                    cur_g = cur_g_base ** cur_pow
                    g_chain.append((cur_index, cur_g))
                    image = cur_num ** cur_g
                    cur_index = image - 1
                    cur_num = image
                    cur_g_base, cur_pow, _ = graph[cur_index]
                rest = ret[cur_index]
                for chain_index, chain_g in reversed(g_chain):
                    rest = chain_g * rest
                    ret[chain_index] = rest   
        return ret
    
    
    def discrete(self):
        #This is not true. Need better condition.
        if len(self.stabaliser_orbits[-1]) == 0:
            return False
        return len(self.stabaliser_orbits[-1]) == 1
    
    def order(self):
        tot = 1
        for orb in self.stabaliser_orbits:
            tot *= len(orb)
        return tot
    
    def orbits(self, level = 0, key = None, in_order = False):
        orbits = []
        visited = [None] * self.degree
        for ele in range(1, self.degree + 1):
            if visited[ele - 1] is None:
                orb = self.orbit(ele, level, key = key)
                orbits.append(orb)
                for orb_ele in orb:    
                    visited[orb_ele - 1] = True
        return orbits
        
    
    def orbit(self, num, level = 0, key = None, in_order = False):
        if level >= len(self.base):
            return [num]
        orb = self._orbit_computation(num, level)
        if in_order:
            ret = sorted(orb, key = key)
        else:
            ret = orb
        return ret
      
    def _orbit_computation(self, num, level):
        # there are better ways to do this. BUt is it too step a price to avoid the hash check.
        gens = self.level_generators(level)
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
    
    def membership_index(self, g, key = None):
        if key is None:
            ordering = self.base + [x for x in range(1, self.degree + 1) if x not in self.base]
            key = ordering_to_key(ordering)
        #divide current order by len of orbit
        #add index used * current order to ret
        
        cand = g
        #sift on level keeping track of which index out of tot
        ret = 0
        cur_order = self.order()
        go_leftmost = False
        
        for cur_level in range(0, len(self.base)):
            cur_orbit = self.stabaliser_orbit(cur_level)
            cur_order //= len(cur_orbit)
            
            image = self.base[cur_level] ** cand
            post_image = self.base[cur_level] ** g
            found = False
            des_index = 0
            for end in cur_orbit:
                if key(end ** g) < key(post_image):
                    des_index += 1
            
            ret += des_index * cur_order            
            
            if image not in cur_orbit:
                break
            
            if not cand.trivial():
                cand = self.sift_on_level(cand, cur_level)
        
        return ret
    
    def element_at_index(self, index, key = None):
        if index < 0 or index >= self.order():
            return None
        if key is None:
            ordering = self.base + [x for x in range(1, self.degree + 1) if x not in self.base]
            key = ordering_to_key(ordering)
        
        ret = self.identity
        
        cur_order = self.order()
        for cur_level in range(0, len(self.base)):
            cur_orbit = self.stabaliser_orbit(cur_level)
            cur_order //= len(cur_orbit)
            des_index = index // cur_order
            index -= des_index * cur_order
            
            #this should be a quick select algorithm if hi performance required.
            image = sorted([(ele ** ret, ele) for ele in cur_orbit], key = lambda x:key(x[0]))[des_index][1]
            inverse = self.stabaliser_representative(image, cur_level)
            if inverse is None:
                raise ValueError("Unexpected orbit violation.")
            ret = (inverse ** (-1)) * ret  
        
        return ret
        
    def element_from_image(self, image):      
        ret = self.identity
        for cur_level in range(0, len(self.base)):
            
            #this should be a quick select algorithm if hi performance required
            des_image = self.base_at_level(cur_level)
            if cur_level < len(image):
                cur_orbit = self.stabaliser_orbit(cur_level)                
                des_image = image[cur_level] ** ret
                if des_image not in cur_orbit:
                    return None
            inverse = self.stabaliser_representative(des_image, cur_level)
            ret = ret * inverse  
        
        return ret ** -1

class DirectSchreierRepresentation():
    def __init__(self, degree):
        self.degree = degree
        self.identity = Permutation.read_cycle_form([], degree)
        self.chain_generators = []
        self.schreier_graphs = []
        #base is needed as a feild.
        self.base = []
        self.stabaliser_orbits = []
    
    def base_at_level(self, level):
        return self.base[level]
    
    def base_till_level(self, level = None):
        if level is None:
            level = len(self.base) 
        return self.base[:level]
        
    def level_generators(self, level):
        return self.chain_generators[level]
    
    def stabaliser_orbit(self, level = 0):
        return self.stabaliser_orbits[level]
    
    def add_to_stabaliser_orbit(self, elements, level = 0):
        self.stabaliser_orbits[level].update(elements)
    
    def _extend_level_single(self, g, level, frontier = None, force_update = False, improve_tree = True):
        #optimisation idea sort the frontier by cost
        updated = False
        graph = self.schreier_graphs[level]
        if frontier is None:
            frontier = self.stabaliser_orbit(level)
        
        new_frontier = []
        visited = [False] * (self.degree + 1)
        updates = []
        for cand in frontier:
            if not visited[cand]:
                cand_cycle = g.element_cycle(cand)
                cycle_size = len(cand_cycle)
                for power, ele in enumerate(cand_cycle):
                    index = ele - 1
                    inverse, _, cost = graph[index]
                    inverse_power = cycle_size - power
                    new_cost = graph[cand - 1][2] + 1
                    if inverse is None:
                        updated = True
                        updates.append((index, (g, inverse_power, new_cost)))
                        new_frontier.append(ele)
                    else:
                        if improve_tree and new_cost < cost:
                            updates.append((index, (g, inverse_power, new_cost)))
                    visited[ele] = True                
                            
        
        #Apply found updates if there is a new element in the orbit
        if updated or force_update:
            for index, node in updates:
                graph[index] = node        
        
        return updated, new_frontier
     
    def extend_level(self, g, level, force_update = False, improve_tree = True):
        #optimisation idea sort the frontier by cost
        frontier = self.stabaliser_orbit(level)
        updated, frontier = self._extend_level_single(g, level, frontier, force_update, improve_tree)
         
        if updated:
            self.add_to_stabaliser_orbit(frontier, level)  
            self.chain_generators[level].append(g)
            additions = [0] * (len(self.chain_generators[level]) - 1) + [len(frontier)]
    
            gen_index = 0
            frontier_index = additions[gen_index]      
            
            while frontier_index < len(frontier):
                #get the current generator
                gen = self.chain_generators[level][gen_index]
                
                #try update the frontier with it (only using unseen points).
                _, new_frontier = self._extend_level_single(gen, level, frontier[frontier_index:], True)
                
                #keep track of how many new points reached
                additions[gen_index] = len(new_frontier)
                
                #update the frontier
                self.add_to_stabaliser_orbit(new_frontier, level)            
                if len(new_frontier) > 0:
                    frontier.extend(new_frontier)
                
                #update the index and the pointer to the new part of frontier.
                gen_index = (gen_index + 1) % len(self.chain_generators[level])
                frontier_index += additions[gen_index]
        elif force_update:
            self.chain_generators[level].append(g)            

        return updated
        
    def add_level(self, base_element):
        self.chain_generators.append([])
        graph = [(None, 1, 0) for _ in range(self.degree)]
        index = base_element - 1
        graph[index] = (self.identity, 1, 0)
        self.schreier_graphs.append(graph)
        self.base.append(base_element)
        self.stabaliser_orbits.append(set([base_element]))
    
    def sift_on_level(self, g, level):
        if level < 0:
            #This indicates we want to sift before stabalising anything.
            return g
        cand = self.base[level] ** g
        inverse = self.stabaliser_representative(cand, level)
        if inverse is None:
            return None
        return g * inverse
    
    def siftee(self, g, level = 0):
        for cur_level in range(level, len(self.base)):
            cand = self.sift_on_level(g, cur_level)
            if cand is None:
                return g
            elif cand.trivial():
                return cand
            g = cand
        return g
    
    def membership(self, g, level = 0):
        cand = self.siftee(g, level)
        return (cand is not None) and cand.trivial()
    
    def __contains__(self, g):
        return self.membership(g)
    
    def __lt__(self, other):
        if isinstance(other, type(self)):
            for self_gen, other_gen in zip(self.canonical_generators(), other.canonical_generators()):
                if self_gen != other_gen:
                    if self_gen < other_gen:
                        return True
                    else:
                        return False
            return False
                        
            
            ##compare base?
            #if self.base != other.base:
                #return self.base < other.base
            
            ##compare orbit sizes/elements
            #for level in range(len(self.base)):
                #self_orb = self.stabaliser_orbit[level]
                #other_orb = other.stabaliser_orbit[level]
                
                #self_min = None                
                #for ele in self_orb:
                    #if ele not in other_orb:
                        #if self_min is None or ele < self_min:
                            #self_min = ele
                
                #other_min = None                
                #for ele in other_orb:
                    #if ele not in self_orb:
                        #if other_min is None or ele < other_min:
                            #other_min = ele
                
                #if self_min is not None and other_min is not None:
                    #return self_min < other_min
                
                #if self_min is not None:
                    #return True
                
                #if other_min is not None:
                    #return False
            
                
            ##compare leftmost branch right most children
        else:
            return NotImplemented
            
    def canonical_generators(self):
        for level in reversed(range(len(self.base))):
            #calc the representative for each image (the fast way).
            #use this to initialise cand
            #should possibly store this sorted.
            madan = True
            for rep in self.transversal(level):
                if rep is not None:
                    if madan:
                        madan = False
                    else:
                        yield self.leftmost_child(rep, level + 1)
    
    def leftmost_child(self, coset_rep, level):
        # 1: if bottom level return cand
        # 2: look at orbits from one level down when acted on by cand
        # 3: take the smallest image and the rep for that image and make cand = rep * cand
        # 4: go1
        cand = coset_rep
        for cur_level in range(level, len(self.base)):
            best_image = None
            best_pre = None
            for pre in self.stabaliser_orbit(cur_level):
                cand_image = pre ** cand
                if best_image is None or cand_image < best_image:
                    best_image = cand_image
                    best_pre = pre
            rep = self.stabaliser_representative(best_pre, cur_level)
            cand = (rep ** -1) * cand
        return cand
    
    def stabaliser_representative(self, image, level):
        """Returns the coset representative inverse for coset associated with 
        the image reachable in the schreier_graph."""
        graph = self.schreier_graphs[level]
        g = self.identity
        cur_index = image - 1
        cur_num = image
        cur_g_base, cur_pow, _ = graph[cur_index]
        if cur_g_base is None:
            return None
        while cur_num != self.base[level]:# and cur_g_base is not None:# and cur_pow > 0:
            cur_g = cur_g_base ** cur_pow
            #Follow the chain to the identity and multiply by the schreier graph element.
            g = g * cur_g
            image = cur_num ** cur_g
            cur_index = image - 1
            cur_num = image
            cur_g_base, cur_pow, _ = graph[cur_index]
        return g

    
    def transversal(self, level):
        #this is the inefficient version.
        #you should store temp paths to do efficiently (as you are stroing them anyway)
        #invs = [self.stabaliser_representative(image, level) for image in range(self.degree, 0, -1)]
        #ret = []
        #for g in reversed(invs):
            #if g is not None:
                #ret.append(g ** -1)
            #else:
                #ret.append(None)
        #return ret
        #better way:
        ret = [None] * self.degree
        for index, g in enumerate(self.transversal_inverses(level)):
            if g is not None:
                ret[index] = g ** -1
        return ret
        
    def transversal_inverses(self, level):
        #initialise ret
        #for each possible value in degree check if graph is None
        #if not follow path back till get to a non none
        ret = [None] * self.degree
        ret[self.base[level] - 1] = self.identity
        graph = self.schreier_graphs[level]
        for image in range(1, self.degree + 1):
            cur_index = image - 1
            cur_num = image
            g_chain = []            
            cur_g_base, cur_pow, _ = graph[cur_index]
            if cur_g_base is not None:    
                while ret[cur_index] is None:
                    cur_g = cur_g_base ** cur_pow
                    g_chain.append((cur_index, cur_g))
                    image = cur_num ** cur_g
                    cur_index = image - 1
                    cur_num = image
                    cur_g_base, cur_pow, _ = graph[cur_index]
                rest = ret[cur_index]
                for chain_index, chain_g in reversed(g_chain):
                    rest = chain_g * rest
                    ret[chain_index] = rest   
        return ret
    
    
    def discrete(self):
        #This is not true. Need better condition.
        if len(self.stabaliser_orbits[-1]) == 0:
            return False
        return len(self.stabaliser_orbits[-1]) == 1
    
    def order(self):
        tot = 1
        for orb in self.stabaliser_orbits:
            tot *= len(orb)
        return tot
    
    def orbits(self, level = 0, key = None, in_order = False):
        orbits = []
        visited = [None] * self.degree
        for ele in range(1, self.degree + 1):
            if visited[ele - 1] is None:
                orb = self.orbit(ele, level, key = key)
                orbits.append(orb)
                for orb_ele in orb:    
                    visited[orb_ele - 1] = True
        return orbits
        
    
    def orbit(self, num, level = 0, key = None, in_order = False):
        if level >= len(self.base):
            return [num]
        orb = self._orbit_computation(num, level)
        if in_order:
            ret = sorted(orb, key = key)
        else:
            ret = orb
        return ret
      
    def _orbit_computation(self, num, level):
        # there are better ways to do this. BUt is it too step a price to avoid the hash check.
        gens = self.level_generators(level)
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
    
    def membership_index(self, g, key = None):
        if key is None:
            ordering = self.base + [x for x in range(1, self.degree + 1) if x not in self.base]
            key = ordering_to_key(ordering)
        #divide current order by len of orbit
        #add index used * current order to ret
        
        cand = g
        #sift on level keeping track of which index out of tot
        ret = 0
        cur_order = self.order()
        go_leftmost = False
        
        for cur_level in range(0, len(self.base)):
            cur_orbit = self.stabaliser_orbit(cur_level)
            cur_order //= len(cur_orbit)
            
            image = self.base[cur_level] ** cand
            post_image = self.base[cur_level] ** g
            found = False
            des_index = 0
            for end in cur_orbit:
                if key(end ** g) < key(post_image):
                    des_index += 1
            
            ret += des_index * cur_order            
            
            if image not in cur_orbit:
                break
            
            if not cand.trivial():
                cand = self.sift_on_level(cand, cur_level)
        
        return ret
    
    def element_at_index(self, index, key = None):
        if index < 0 or index >= self.order():
            return None
        if key is None:
            ordering = self.base + [x for x in range(1, self.degree + 1) if x not in self.base]
            key = ordering_to_key(ordering)
        
        ret = self.identity
        
        cur_order = self.order()
        for cur_level in range(0, len(self.base)):
            cur_orbit = self.stabaliser_orbit(cur_level)
            cur_order //= len(cur_orbit)
            des_index = index // cur_order
            index -= des_index * cur_order
            
            #this should be a quick select algorithm if hi performance required.
            image = sorted([(ele ** ret, ele) for ele in cur_orbit], key = lambda x:key(x[0]))[des_index][1]
            inverse = self.stabaliser_representative(image, cur_level)
            if inverse is None:
                raise ValueError("Unexpected orbit violation.")
            ret = (inverse ** (-1)) * ret  
        
        return ret
        
    def element_from_image(self, image):      
        ret = self.identity
        for cur_level in range(0, len(self.base)):
            
            #this should be a quick select algorithm if hi performance required
            des_image = self.base_at_level(cur_level)
            if cur_level < len(image):
                cur_orbit = self.stabaliser_orbit(cur_level)                
                des_image = image[cur_level] ** ret
                if des_image not in cur_orbit:
                    return None
            inverse = self.stabaliser_representative(des_image, cur_level)
            ret = ret * inverse  
        
        return ret ** -1
    
        
    

def membership_siftee(candidate, schreier_graphs, base, identity):
    """Returns the sifftee when chaining using the schreier graphs and the given base."""
    for num, schreier_graph in zip(base, schreier_graphs):
        image = num**candidate
        #We used to construct all coset inverses this is bad we only need one.
        #image_index = image - 1
        #coset_inverses = _coset_rep_inverses(schreier_graph)
        #coset_rep = coset_inverses[image_index]
        coset_rep = _coset_rep_inverse(image, schreier_graph, identity)
        if coset_rep is None:
            return candidate
        else:
            candidate = candidate * coset_rep
    return candidate

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

def naive_schreier_sims_algorithm(generators, identity):
    """Test algorithm for understanding."""
    chain_generators = [generators]
    schreier_graphs = []
    try:
        gen = next(gen for gen in chain_generators[0] if gen != identity)
    except(StopIteration):
        return [],[],[],[]
    first_non_fixed = next(num for num in range(1, len(identity) + 1) if num**gen != num)
    base = [first_non_fixed]
    finished = False
    while not finished:
        num = base[-1]
        gens = chain_generators[-1]
        schreier_graph = _schreier_graph(num, gens, identity)
        coset_reps = _coset_reps(schreier_graph, identity)
        schreier_gens = _schreier_generators(num, coset_reps, gens, identity)
        chain_generators.append(schreier_gens) #make next level.
        schreier_graphs.append(schreier_graph)
        
        if len(schreier_gens) > 0:
            gen = schreier_gens[0]
            first_non_fixed = next(num for num in range(1, len(identity) + 1) if num**gen != num)
            base.append(first_non_fixed)
        else:
            finished = True
        
    strong_gens = []
    unique_check = set()
    for gens in chain_generators:
        for gen in gens:
            if gen not in unique_check:
                strong_gens.append(gen)
                unique_check.add(gen)
    
    return base, strong_gens, chain_generators, schreier_graphs

def cleaner_schreier_sims_algorithm(generators, identity):
    """Returns a base, a strong generating list, a list of lists of the 
    subgroup chain generators and the schreier trees for the given generators."""
    chain_generators = [generators]
    chain_schreier_generators = [None]
    schreier_graphs = [None]
    try:
        gen = next(gen for gen in chain_generators[0] if gen != identity)
    except(StopIteration):
        return [],[],[],[]
    first_non_fixed = next(num for num in range(1, len(identity) + 1) if num**gen != num)
    base = [first_non_fixed]
    level = 0
    while level > -1:
        schreier_gens = chain_schreier_generators[level]
        if schreier_gens is None: #first time at this level
            num = base[level]
            gens = chain_generators[level]
            #unnecciary? if schreier_graph is None: #populate for first time
            schreier_graph = _schreier_graph(num, gens, identity)
            schreier_graphs[level] = schreier_graph
            coset_reps = _coset_reps(schreier_graph, identity)
            # need in reverse order as they will be popped off. Not strictly nec.
            schreier_gens = list(reversed(_schreier_generators(num, coset_reps, gens, identity)))
            chain_schreier_generators[level] = schreier_gens
            
            chain_generators.append([]) #make next level.
            chain_schreier_generators.append(None)
            schreier_graphs.append([])
        
        elif len(schreier_gens) == 0: #have previously exhausted this level
            num = base[level]
            schreier_graph = schreier_graphs[level]
            gens = chain_generators[level]
            _schreier_graph_expand(schreier_graph, gens, len(gens) - 1)
            coset_reps = _coset_reps(schreier_graph, identity)
            schreier_gens = list(reversed(_schreier_generators(num, coset_reps, gens[-1:], identity)))
            chain_schreier_generators[level] = schreier_gens
        
        membership_pass = True #have we passed all membership tests?            
        
        while membership_pass and len(schreier_gens) > 0:
            gen = schreier_gens.pop()
            schreier_graphs_membership = schreier_graphs[level+1:]
            base_membership = base[level+1:] 
            siftee = membership_siftee(gen, schreier_graphs_membership, base_membership, identity)
            if siftee != identity:
                membership_pass = False
                chain_generators[level+1].append(siftee)
                if len(base) == level + 1: #also need to add to base.
                    first_non_fixed = next(num for num in range(1, len(identity) + 1) if num**siftee != num)
                    base.append(first_non_fixed)                        
        
        if membership_pass: #exhausted this level so check for next schreier gen of prior level.
            level = level - 1
            
        else: #needed to add to the generators so need to check down recursively.
            level = level + 1
    
    strong_gens = []
    unique_check = set()
    for gens in chain_generators:
        for gen in gens:
            if gen not in unique_check:
                strong_gens.append(gen)
                unique_check.add(gen)
    
    return base, strong_gens, chain_generators, schreier_graphs[:-1]

def schreier_sims_algorithm(generators, identity):
    """Returns a base, a strong generating list, a list of lists of the 
    subgroup chain generators and the schreier trees for the given generators."""
    chain_generators = [generators]
    chain_schreier_generators = [None]
    schreier_graphs = [None]
    try:
        gen = next(gen for gen in chain_generators[0] if gen != identity)
    except(StopIteration):
        return [],[],[],[]
    first_non_fixed = next(num for num in range(1, len(identity) + 1) if num**gen != num)
    base = [first_non_fixed]
    level = 0
    while level > -1:
        schreier_gens = chain_schreier_generators[level]
        if schreier_gens is None: #first time at this level
            num = base[level]
            gens = chain_generators[level]
            #unnecciary? if schreier_graph is None: #populate for first time
            schreier_graph = _schreier_graph(num, gens, identity)
            schreier_graphs[level] = schreier_graph
            coset_reps = _coset_reps(schreier_graph, identity)
            # need in reverse order as they will be popped off. Not strictly nec.
            schreier_gens = list(reversed(_schreier_generators(num, coset_reps, gens, identity)))
            chain_schreier_generators[level] = schreier_gens
            
            chain_generators.append([]) #make next level.
            chain_schreier_generators.append(None)
            schreier_graphs.append([])
        
        elif len(schreier_gens) == 0: #have previously exhausted this level
            num = base[level]
            schreier_graph = schreier_graphs[level]
            gens = chain_generators[level]
            _schreier_graph_expand(schreier_graph, gens, len(gens) - 1)
            coset_reps = _coset_reps(schreier_graph, identity)
            schreier_gens = list(reversed(_schreier_generators(num, coset_reps, gens[-1:], identity)))
            chain_schreier_generators[level] = schreier_gens
        
        membership_pass = True #have we passed all membership tests?            
        
        while membership_pass and len(schreier_gens) > 0:
            gen = schreier_gens.pop()
            schreier_graphs_membership = schreier_graphs[level+1:]
            base_membership = base[level+1:] 
            siftee = membership_siftee(gen, schreier_graphs_membership, base_membership, identity)
            if siftee != identity:
                membership_pass = False
                chain_generators[level+1].append(siftee)
                if len(base) == level + 1: #also need to add to base.
                    first_non_fixed = next(num for num in range(1, len(identity) + 1) if num**siftee != num)
                    base.append(first_non_fixed)                        
        
        if membership_pass: #exhausted this level so check for next schreier gen of prior level.
            level = level - 1
            
        else: #needed to add to the generators so need to check down recursively.
            level = level + 1
    
    strong_gens = []
    unique_check = set()
    for gens in chain_generators:
        for gen in gens:
            if gen not in unique_check:
                strong_gens.append(gen)
                unique_check.add(gen)
    
    return base, strong_gens, chain_generators, schreier_graphs[:-1]

def schreier_sims_algorithm_fixed_base(generators, base_cand, identity):
    """Returns a base, a strong generating list, a list of lists of the 
    subgroup chain generators and the schreier trees for the given generators.
    The base will be a prefix of base_cand or will be an extention of base 
    cand."""
    chain_generators = [generators]
    chain_schreier_generators = [None]
    schreier_graphs = [None]
    try:
        gen = next(gen for gen in chain_generators[0] if gen != identity)
    except(StopIteration):
        return [],[],[],[]
    base = []
    base.append(base_point(base, base_cand, gen, identity))
    level = 0
    while level > -1:
        schreier_gens = chain_schreier_generators[level]
        if schreier_gens is None: #first time at this level
            num = base[level]
            gens = chain_generators[level]
            #unnecciary? if schreier_graph is None: #populate for first time
            schreier_graph = _schreier_graph(num, gens, identity)
            schreier_graphs[level] = schreier_graph
            coset_reps = _coset_reps(schreier_graph, identity)
            # need in reverse order as they will be popped off. Not strictly nec.
            schreier_gens = list(reversed(_schreier_generators(num, coset_reps, gens, identity)))
            chain_schreier_generators[level] = schreier_gens
            
            chain_generators.append([]) #make next level.
            chain_schreier_generators.append(None)
            schreier_graphs.append([])
        
        elif len(schreier_gens) == 0: #have previously exhausted this level
            num = base[level]
            schreier_graph = schreier_graphs[level]
            gens = chain_generators[level]
            _schreier_graph_expand(schreier_graph, gens, len(gens) - 1)
            coset_reps = _coset_reps(schreier_graph, identity)
            schreier_gens = list(reversed(_schreier_generators(num, coset_reps, gens[-1:], identity)))
            chain_schreier_generators[level] = schreier_gens
        
        membership_pass = True #have we passed all membership tests?            
        
        while membership_pass and len(schreier_gens) > 0:
            gen = schreier_gens.pop()
            schreier_graphs_membership = schreier_graphs[level+1:]
            base_membership = base[level+1:] 
            siftee = membership_siftee(gen, schreier_graphs_membership, base_membership, identity)
            if siftee != identity:
                membership_pass = False
                chain_generators[level+1].append(siftee)
                if len(base) == level + 1: #also need to add to base.
                    first_non_fixed = next(num for num in range(1, len(identity) + 1) if num**siftee != num)                
                    base.append(base_point(base, base_cand, siftee, identity))                        
        
        if membership_pass: #exhausted this level so check for next schreier gen of prior level.
            level = level - 1
            
        else: #needed to add to the generators so need to check down recursively.
            level = level + 1
    
    strong_gens = []
    unique_check = set()
    for gens in chain_generators:
        for gen in gens:
            if gen not in unique_check:
                strong_gens.append(gen)
                unique_check.add(gen)
    
    return base, strong_gens, chain_generators, schreier_graphs[:-1]

def base_point(base, base_cand, siftee, identity):
    index = len(base)
    if index < len(base_cand):
        return base_cand[index]
    else:
        first_non_fixed = next(num for num in range(1, len(identity) + 1) if num**siftee != num)
        return first_non_fixed


class SchreierStructureLegacy():
    def __init__(self, degree):
        self.degree = degree
        self.identity = Permutation.read_cycle_form([], degree)
        self.chain_generators = []
        self.schreier_graphs = []
        #base is needed as a feild.
        self.base = []
        self.stabaliser_orbits = []
    
    def base_at_level(self, level):
        return self.base[level]
    
    def base_till_level(self, level = None):
        if level is None:
            level = len(self.base) 
        return self.base[:level]
        
    def level_generators(self, level):
        return self.chain_generators[level]
    
    def stabaliser_orbit(self, level = 0):
        return self.stabaliser_orbits[level]
    
    def add_to_stabaliser_orbit(self, elements, level = 0):
        self.stabaliser_orbits[level].update(elements)
    
    def _extend_level_single(self, g, level, frontier = None, force_update = False, improve_tree = True):
        #optimisation idea sort the frontier by cost
        updated = False
        graph = self.schreier_graphs[level]
        if frontier is None:
            frontier = self.stabaliser_orbit(level)
        
        new_frontier = []
        visited = [False] * (self.degree + 1)
        updates = []
        for cand in frontier:
            if not visited[cand]:
                cand_cycle = g.element_cycle(cand)
                cycle_size = len(cand_cycle)
                for power, ele in enumerate(cand_cycle):
                    index = ele - 1
                    inverse, _, cost = graph[index]
                    inverse_power = cycle_size - power
                    new_cost = graph[cand - 1][2] + 1
                    if inverse is None:
                        updated = True
                        updates.append((index, (g, inverse_power, new_cost)))
                        new_frontier.append(ele)
                    else:
                        if improve_tree and new_cost < cost:
                            updates.append((index, (g, inverse_power, new_cost)))
                    visited[ele] = True                
                            
        
        #Apply found updates if there is a new element in the orbit
        if updated or force_update:
            for index, node in updates:
                graph[index] = node        
        
        return updated, new_frontier
     
    def extend_level(self, g, level, force_update = False, improve_tree = True):
        #optimisation idea sort the frontier by cost
        frontier = self.stabaliser_orbit(level)
        updated, frontier = self._extend_level_single(g, level, frontier, force_update, improve_tree)
         
        if updated:
            self.add_to_stabaliser_orbit(frontier, level)  
            self.chain_generators[level].append(g)
            additions = [0] * (len(self.chain_generators[level]) - 1) + [len(frontier)]
    
            gen_index = 0
            frontier_index = additions[gen_index]      
            
            while frontier_index < len(frontier):
                #get the current generator
                gen = self.chain_generators[level][gen_index]
                
                #try update the frontier with it (only using unseen points).
                _, new_frontier = self._extend_level_single(gen, level, frontier[frontier_index:], True)
                
                #keep track of how many new points reached
                additions[gen_index] = len(new_frontier)
                
                #update the frontier
                self.add_to_stabaliser_orbit(new_frontier, level)            
                if len(new_frontier) > 0:
                    frontier.extend(new_frontier)
                
                #update the index and the pointer to the new part of frontier.
                gen_index = (gen_index + 1) % len(self.chain_generators[level])
                frontier_index += additions[gen_index]
        elif force_update:
            self.chain_generators[level].append(g)            

        return updated
        
    def add_level(self, base_element):
        self.chain_generators.append([])
        graph = [(None, 1, 0) for _ in range(self.degree)]
        index = base_element - 1
        graph[index] = (self.identity, 1, 0)
        self.schreier_graphs.append(graph)
        self.base.append(base_element)
        self.stabaliser_orbits.append(set([base_element]))
    
    def sift_on_level(self, g, level):
        if level < 0:
            #This indicates we want to sift before stabalising anything.
            return g
        cand = self.base[level] ** g
        inverse = self.stabaliser_representative(cand, level)
        if inverse is None:
            return None
        return g * inverse
    
    def siftee(self, g, level = 0):
        for cur_level in range(level, len(self.base)):
            cand = self.sift_on_level(g, cur_level)
            if cand is None:
                return g
            elif cand.trivial():
                return cand
            g = cand
        return g
    
    def membership(self, g, level = 0):
        cand = self.siftee(g, level)
        return (cand is not None) and cand.trivial()
    
    def __contains__(self, g):
        return self.membership(g)
    
    def __lt__(self, other):
        if isinstance(other, type(self)):
            for self_gen, other_gen in zip(self.canonical_generators(), other.canonical_generators()):
                if self_gen != other_gen:
                    if self_gen < other_gen:
                        return True
                    else:
                        return False
            return False
                        
            
            ##compare base?
            #if self.base != other.base:
                #return self.base < other.base
            
            ##compare orbit sizes/elements
            #for level in range(len(self.base)):
                #self_orb = self.stabaliser_orbit[level]
                #other_orb = other.stabaliser_orbit[level]
                
                #self_min = None                
                #for ele in self_orb:
                    #if ele not in other_orb:
                        #if self_min is None or ele < self_min:
                            #self_min = ele
                
                #other_min = None                
                #for ele in other_orb:
                    #if ele not in self_orb:
                        #if other_min is None or ele < other_min:
                            #other_min = ele
                
                #if self_min is not None and other_min is not None:
                    #return self_min < other_min
                
                #if self_min is not None:
                    #return True
                
                #if other_min is not None:
                    #return False
            
                
            ##compare leftmost branch right most children
        else:
            return NotImplemented
            
    def canonical_generators(self):
        for level in reversed(range(len(self.base))):
            #calc the representative for each image (the fast way).
            #use this to initialise cand
            #should possibly store this sorted.
            madan = True
            for rep in self.transversal(level):
                if rep is not None:
                    if madan:
                        madan = False
                    else:
                        yield self.leftmost_child(rep, level + 1)
    
    def leftmost_child(self, coset_rep, level):
        # 1: if bottom level return cand
        # 2: look at orbits from one level down when acted on by cand
        # 3: take the smallest image and the rep for that image and make cand = rep * cand
        # 4: go1
        cand = coset_rep
        for cur_level in range(level, len(self.base)):
            best_image = None
            best_pre = None
            for pre in self.stabaliser_orbit(cur_level):
                cand_image = pre ** cand
                if best_image is None or cand_image < best_image:
                    best_image = cand_image
                    best_pre = pre
            rep = self.stabaliser_representative(best_pre, cur_level)
            cand = (rep ** -1) * cand
        return cand
    
    def stabaliser_representative(self, image, level):
        """Returns the coset representative inverse for coset associated with 
        the image reachable in the schreier_graph."""
        graph = self.schreier_graphs[level]
        g = self.identity
        cur_index = image - 1
        cur_num = image
        cur_g_base, cur_pow, _ = graph[cur_index]
        if cur_g_base is None:
            return None
        while cur_num != self.base[level]:# and cur_g_base is not None:# and cur_pow > 0:
            cur_g = cur_g_base ** cur_pow
            #Follow the chain to the identity and multiply by the schreier graph element.
            g = g * cur_g
            image = cur_num ** cur_g
            cur_index = image - 1
            cur_num = image
            cur_g_base, cur_pow, _ = graph[cur_index]
        return g

    
    def transversal(self, level):
        #this is the inefficient version.
        #you should store temp paths to do efficiently (as you are stroing them anyway)
        #invs = [self.stabaliser_representative(image, level) for image in range(self.degree, 0, -1)]
        #ret = []
        #for g in reversed(invs):
            #if g is not None:
                #ret.append(g ** -1)
            #else:
                #ret.append(None)
        #return ret
        #better way:
        ret = [None] * self.degree
        for index, g in enumerate(self.transversal_inverses(level)):
            if g is not None:
                ret[index] = g ** -1
        return ret
        
    def transversal_inverses(self, level):
        #initialise ret
        #for each possible value in degree check if graph is None
        #if not follow path back till get to a non none
        ret = [None] * self.degree
        ret[self.base[level] - 1] = self.identity
        graph = self.schreier_graphs[level]
        for image in range(1, self.degree + 1):
            cur_index = image - 1
            cur_num = image
            g_chain = []            
            cur_g_base, cur_pow, _ = graph[cur_index]
            if cur_g_base is not None:    
                while ret[cur_index] is None:
                    cur_g = cur_g_base ** cur_pow
                    g_chain.append((cur_index, cur_g))
                    image = cur_num ** cur_g
                    cur_index = image - 1
                    cur_num = image
                    cur_g_base, cur_pow, _ = graph[cur_index]
                rest = ret[cur_index]
                for chain_index, chain_g in reversed(g_chain):
                    rest = chain_g * rest
                    ret[chain_index] = rest   
        return ret
    
    
    def discrete(self):
        #This is not true. Need better condition.
        if len(self.stabaliser_orbits[-1]) == 0:
            return False
        return len(self.stabaliser_orbits[-1]) == 1
    
    def order(self):
        tot = 1
        for orb in self.stabaliser_orbits:
            tot *= len(orb)
        return tot
    
    def orbits(self, level = 0, key = None, in_order = False):
        orbits = []
        visited = [None] * self.degree
        for ele in range(1, self.degree + 1):
            if visited[ele - 1] is None:
                orb = self.orbit(ele, level, key = key)
                orbits.append(orb)
                for orb_ele in orb:    
                    visited[orb_ele - 1] = True
        return orbits
        
    
    def orbit(self, num, level = 0, key = None, in_order = False):
        if level >= len(self.base):
            return [num]
        orb = self._orbit_computation(num, level)
        if in_order:
            ret = sorted(orb, key = key)
        else:
            ret = orb
        return ret
      
    def _orbit_computation(self, num, level):
        # there are better ways to do this. BUt is it too step a price to avoid the hash check.
        gens = self.level_generators(level)
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
    
    def membership_index(self, g, key = None):
        if key is None:
            ordering = self.base + [x for x in range(1, self.degree + 1) if x not in self.base]
            key = ordering_to_key(ordering)
        #divide current order by len of orbit
        #add index used * current order to ret
        
        cand = g
        #sift on level keeping track of which index out of tot
        ret = 0
        cur_order = self.order()
        go_leftmost = False
        
        for cur_level in range(0, len(self.base)):
            cur_orbit = self.stabaliser_orbit(cur_level)
            cur_order //= len(cur_orbit)
            
            image = self.base[cur_level] ** cand
            post_image = self.base[cur_level] ** g
            found = False
            des_index = 0
            for end in cur_orbit:
                if key(end ** g) < key(post_image):
                    des_index += 1
            
            ret += des_index * cur_order            
            
            if image not in cur_orbit:
                break
            
            if not cand.trivial():
                cand = self.sift_on_level(cand, cur_level)
        
        return ret
    
    def element_at_index(self, index, key = None):
        if index < 0 or index >= self.order():
            return None
        if key is None:
            ordering = self.base + [x for x in range(1, self.degree + 1) if x not in self.base]
            key = ordering_to_key(ordering)
        
        ret = self.identity
        
        cur_order = self.order()
        for cur_level in range(0, len(self.base)):
            cur_orbit = self.stabaliser_orbit(cur_level)
            cur_order //= len(cur_orbit)
            des_index = index // cur_order
            index -= des_index * cur_order
            
            #this should be a quick select algorithm if hi performance required.
            image = sorted([(ele ** ret, ele) for ele in cur_orbit], key = lambda x:key(x[0]))[des_index][1]
            inverse = self.stabaliser_representative(image, cur_level)
            if inverse is None:
                raise ValueError("Unexpected orbit violation.")
            ret = (inverse ** (-1)) * ret  
        
        return ret
        
    def element_from_image(self, image):      
        ret = self.identity
        for cur_level in range(0, len(self.base)):
            
            #this should be a quick select algorithm if hi performance required
            des_image = self.base_at_level(cur_level)
            if cur_level < len(image):
                cur_orbit = self.stabaliser_orbit(cur_level)                
                des_image = image[cur_level] ** ret
                if des_image not in cur_orbit:
                    return None
            inverse = self.stabaliser_representative(des_image, cur_level)
            ret = ret * inverse  
        
        return ret ** -1
