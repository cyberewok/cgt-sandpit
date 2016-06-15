from permutation import Permutation

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

def _coset_rep_inverse(image, schreier_graph, identity):
    """Returns the coset representative inverse for coset associated with 
    the image reachable in the schreier_graph."""
    g = identity
    cur_index = image - 1
    cur_num = image
    cur_g = schreier_graph[cur_index]
    while cur_g is not None and cur_g != identity:
        #Follow the chain to the identity and multiply by the schreier graph element.
        g = g * cur_g
        image = cur_num**cur_g                    
        cur_index = image - 1
        cur_num = image
        cur_g = schreier_graph[cur_index]
    if cur_g is None:
        return None
    return g

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
            schreier_graph = schreier_graphs[level]
            gens = chain_generators[level]
            #unnecciary? if schreier_graph is None: #populate for first time
            schreier_graph = _schreier_graph(num, gens, identity)
            schreier_graphs[level] = schreier_graph
            coset_reps = _coset_reps(schreier_graph, identity)
            # need in reverse order as they will be popped off.
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