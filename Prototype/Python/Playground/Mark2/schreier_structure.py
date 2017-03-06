from permutation import Permutation
from ordering import ordering_to_key
from random import randrange
from math import log2

class RandomGenerator():
    
    def element(self):
        pass
    
    def add(self):
        pass

class ProductReplacer(RandomGenerator):
    def __init__(self, seed_gens):
        self.seed_gens = [gen for gen in seed_gens]
        self.degree = len(self.seed_gens[0])
        self.rand = lambda : randrange(len(seed_gens))
        self.rand_deg = lambda : randrange(len(seed_gens))        
        while len(self.seed_gens) < log2(self.degree)*2:
            self.seed_gens.append(self.seed_gens[self.rand()]**self.rand_deg())
        self.initialise(30*len(self.seed_gens))
    
    def initialise(self, num_rolls):
        for _ in range(num_rolls):
            self.element()
    
    def add(self, ele):
        self.seed_gens.append(ele)
    
    def element(self):

        if len(self.seed_gens) == 1:
            return self.seed_gens[0]        
        i = self.rand()
        j = self.rand()
        while i==j:
            j = self.rand()
        self.seed_gens[j] = self.seed_gens[i] * self.seed_gens[j]
        return self.seed_gens[j]

class RandomSubproduct(RandomGenerator):
    def __init__(self, seed_gens):
        self.seed_gens = seed_gens
        self.degree = len(self.seed_gens[0])
        self.identity = Permutation.read_cycle_form([], self.degree)
        self.rand = lambda : randrange(2)
    
    def add(self, ele):
        self.seed_gens.append(ele)
    
    def element(self):
        tot = self.identity
        for gen in self.seed_gens:
            if self.rand():
                tot = tot * gen
        return tot

class SchreierStructure():
    def __init__(self, degree):
        self.degree = degree
        self.identity = Permutation.read_cycle_form([], degree)
        self.chain_generators = []
        self.schreier_graphs = []
        self.base = []
        self.stabaliser_orbits = []
    
    def base_till_level(self, level = None):
        if level is None:
            level = len(self.base) 
        return self.base[:level]
        
    def level_generators(self, level):
        self.chain_schreier_generators[level]
    
    def stabaliser_orbit(self, level = 0):
        return self.stabaliser_orbits[level]
    
    def add_to_stabaliser_orbit(self, elements, level = 0):
        self.stabaliser_orbits[level].update(elements)
    
    def _extend_level_single(self, g, level, frontier = None, force_update = False):
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
                        if new_cost < cost:
                            updates.append((index, (g, inverse_power, new_cost)))
                    visited[ele] = True                
                            
        
        #Apply found updates if there is a new element in the orbit
        if updated or force_update:
            for index, node in updates:
                graph[index] = node        
        
        return updated, new_frontier
     
    def extend_level(self, g, level):
        #optimisation idea sort the frontier by cost
        frontier = self.stabaliser_orbit(level)
        updated, frontier = self._extend_level_single(g, level, frontier, False)
         
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
    
    def sift(self, g):
        for level in range(len(self.base)):
            g = self.sift_on_level(g, level)
            if g is None:
                return None
            elif g.trivial():
                return g
        return g
    
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
    
    def discrete(self):
        if len(self.stabaliser_orbits[-1]) == 0:
            return False
        return len(self.stabaliser_orbits[-1]) == 1
    
    def order(self):
        tot = 1
        for orb in self.stabaliser_orbits:
            tot *= len(orb)
        return tot

class RandomSchreierGenerator():
    def __init__(self, generators, base = None, group_order = None, element_generator_constructor = None):
        if len(generators) == 0:
            raise ValueError("Must define atleast one generator.")
        self.generators = generators
        self.degree = len(generators[0])
        self.base_candidate = base
        if self.base_candidate is None:
            self.base_candidate = []
        self.group_order = group_order
        if element_generator_constructor is None:
            element_generator_constructor = ProductReplacer
        self.rand_factory = element_generator_constructor
        self.rand = self.rand_factory(self.generators)
        self.level_complete = []
        self.depth = 0
        self.structure = SchreierStructure(self.degree)
        
    def complete(self, confidence = .999, trials = None):
        self.verify_till_level(self.degree, confidence, trials)
    
    def complete_till_level(self, level, confidence = .999, trials = None):
        self.verify_till_level(level, confidence, trials)
    
    def verify_till_level(self, level, confidence = .999, trials = None):
        
        if trials is None:
            trials = log2(1/(1-confidence))
        
        passes = 0
        ret = True

        if self.group_order is not None and self.structure.order() == self.group_order:
            return ret        

        while passes < trials:
            cand = self.rand.element()
            
            if self.sift_till_level(cand, level):
                passes += 1
            else:
                ret = False
                passes = 0
                if self.group_order is not None and self.structure.order() == self.group_order:
                    return ret
        return ret
        
    def sift_till_level(self, cand, level, start_level = 0):

        
        for cur_level in range(start_level, level):
            if cur_level == self.depth:
                self.add_level(cand)
          
            siftee = self.structure.sift_on_level(cand, cur_level)
            
            if siftee is None:
                self.structure.extend_level(cand, cur_level)
                return False
            
            if siftee.trivial():
                return True
            
            cand = siftee
        
        return True

    def add_level(self, cand):
        self.level_complete.append(False)
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
    

class NearlyLinearSchreierGenerator():
    def __init__(self, generators, base = None, group_order = None, element_generator_constructor = None):
        if len(generators) == 0:
            raise ValueError("Must define atleast one generator.")
        self.generators = generators
        self.degree = len(generators[0])
        self.base_candidate = base
        if self.base_candidate is None:
            self.base_candidate = []
        self.group_order = group_order
        if element_generator_constructor is None:
            element_generator_constructor = RandomSubproduct
        self.rand_factory = element_generator_constructor
        self.rand = [self.rand_factory(self.generators)]
        self.level_complete = []
        self.depth = 0
        self.structure = SchreierStructure(self.degree)
    
    def populate_level(self, level,  trials = 1):
        fails = 0
        while fails < trials:
            #Generate a random element from the level above.
            cand = rand[level].element()
            #Multiply by the inverse in the schreier vector.
            stab_cand = structure.sift_on_level(cand, level - 1)
            #Check if the element provides anything new.
            #If it does update the schreier vector with all it's shorter paths
            #Keep track of the number of distinct elements stored.
            #If no new elements stop orbiting
            is_bigger = structure.add_to_level(stab_cand, level)
            if is_bigger:
                fails = 0
                self.rand[level + 1].add(stab_cand)
            else:
                fails += 1
    
    def complete_till_level(self, level, confidence = .99, trials = None):
        
        for cur_level in range(level):
            if cur_level == self.depth:
                self.add_level()

            if not self.level_complete[cur_level]:                
                self.populate_level(level)
                self.level_complete[cur_level] = True
            
            if self.structure.discrete():
                break
        
        self.verify_till_level(level, confidence, trials)
    
    def verify_till_level(self, level, confidence = .99, tials = None):
        if self.group_order is not None and self.structure.discrete():
            if self.group_order == self.structure.order():
                return True
        
        if trials is None:
            trials = log2(1/(1-confidence))
        
        passes = 0
        ret = True
        while passes < trials:
            if self.sift_till_level(level):
                passes += 1
            else:
                ret = False
                passes = 0
        return ret
        
    def sift_till_level(self, level, start_level = 0):

        cand = rand[start_level].element()
        for cur_level in range(start_level, level):
            if cur_level == self.depth:
                add_level()
          
            siftee = structure.sift_on_level(cand, cur_level)
            
            if siftee is None:
                structure.add_to_level(cand, cur_level)
                return False
            
            if siftee.trivial():
                return True
            
            cand = siftee
        
        return True
            
        
                
    def add_level(self):
        self.level_complete.append(False)
        if self.depth == 0:
            gens = self.generators
        else:
            gens = self.structure.level_generators(depth - 1)
        self.rand.append(self.rand_factory(gens))
        new_base_ele = self.extend_base(gens[0])
        self.structure.add_level(new_base_ele)
        self.depth += 1
        
    def extend_base(self,non_id):
        index = len(self.structure.base)
        if index < len(self.base_candidate):
            new_element = self.base_candidate[index]
            return new_element
        else:
            first_non_fixed = next(num for num in range(1, len(self.identity) + 1) if num**non_id != num)
            
            return first_non_fixed
    
def _schreier_graph(num, edges, identity):
    """Calculates the schreier graph for the group defined by the generator list
    edges with respect to subgroup stabalised by the base set element num.
    Also needs a copy of the identity element."""
    #Num is the fixed element of the base set that G acts on.
    #Edges are the generators for previous subgroup.
    schreier_graph = [None for _ in range(len(identity))]
    schreier_graph[num - 1] = identity
    return _schreier_graph_expand(schreier_graph, edges, 0)

def _schreier_graph_expand(schreier_graph, edges, new_edge_index):
    """Given a schreier graph accurate for the generators upto the 
    new_edge_index this function extends the schreier graph. Note the 
    schreier_graph parameter is modified in place AND returned."""
    #New edge index is the index from which all generators after that index have not yet been considered, i.e., are new.
    #Inverses are needed to calculate images as the path to the identity has to be in terms of generators (to save space). 
    edges_inv = [g**-1 for g in edges]
    #The orbit of the fixed set element (note we dont need to know this element explicitly).
    old_frontier = [i + 1 for i, g in enumerate(schreier_graph) if g is not None]
    new_frontier = []
    cur_index = 0
    for num in old_frontier:
        #Try each of the new edges to get a new point from the set.
        for g, g_inv in zip(edges[new_edge_index:], edges_inv[new_edge_index:]):
            image = num**g_inv
            if schreier_graph[image - 1] is None:
                #Found a new point (we havent been to this entry in the graph before)!
                schreier_graph[image - 1] = g
                new_frontier.append(image)
    while len(new_frontier) > 0:
        #While there are still points to explore.
        cur_num = new_frontier.pop()
        for g, g_inv in zip(edges, edges_inv):
            #Try all the edges.
            image = cur_num**g_inv
            if schreier_graph[image - 1] is None:
                #New point found
                schreier_graph[image - 1] = g
                new_frontier.append(image)
    return schreier_graph    

def _coset_rep_inverses(schreier_graph, identity):
    """Constructs the coset representative inverses for each coset
    reachable in the schreier_graph. Needs the identity."""
    coset_reps = [None for _ in schreier_graph]
    coset_reps[schreier_graph.index(identity)] = identity
    for index in [i for i, v in enumerate(schreier_graph) if v is not None]:
        #Iterates over all indices of reachable cosets in the schreier_graph.
        indices_to_coset = [index] #the path back to known cosets.
        while coset_reps[indices_to_coset[-1]] is None:
            #Populates the indices of a path back to a known coset.
            cur_index = indices_to_coset[-1]
            cur_g = schreier_graph[cur_index]
            cur_num = (cur_index + 1)
            image = cur_num**cur_g
            image_index = image - 1
            indices_to_coset.append(image_index)
        #The last index is a known coset so we do not need to know the generator there.
        prev_index = indices_to_coset.pop()
        while len(indices_to_coset) > 0:
            #Pop the last index and update the list of known cosets
            cur_index = indices_to_coset.pop()
            coset_reps[cur_index] = schreier_graph[cur_index] * coset_reps[prev_index]
            prev_index = cur_index
    #return the list coset representative inverses found.
    return coset_reps    

def _coset_reps(schreier_graph, identity):
    """Constructs a list of coset leaders for the given schreier graph."""
    coset_reps = []
    inv = _coset_rep_inverses(schreier_graph, identity)
    for g in inv:
        if g is not None:
            coset_reps.append(g**-1)
        else:
            coset_reps.append(None)
    return coset_reps



def _schreier_generators(num, coset_reps, edges, identity):
    """Returns the schreier generators for the subgroup that stabilises num."""
    schreier_gens = []
    unique_check = {identity}
    for r in [g for g in coset_reps if g is not None]:
        for s in edges:
            rs = r * s
            rs_coset_index = (num**rs) - 1
            rs_coset_rep = coset_reps[rs_coset_index]
            gen = rs * rs_coset_rep**-1
            if gen not in unique_check:    
                schreier_gens.append(gen)
                unique_check.add(gen)
    return schreier_gens

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

def group_size(schreier_graphs):
    total = 1
    for num_cosets in [len([g for g in sg if g is not None]) for sg in schreier_graphs]:
        total *= num_cosets
    return total  

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
        