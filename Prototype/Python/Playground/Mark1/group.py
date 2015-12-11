from permutation import Permutation

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
    def __init__(self, generators = None, base = None):
        if generators is None or len(generators) == 0:
            self.identity = Permutation([])
        else:
            g = generators[0]
            self.identity = g**-1 * g
        if base is None:
            self.base = []
        else:
            self.base = base
        self.chain_generators = None
        self.schreier_graphs = None
        super().__init__(None, generators, self.identity, self.identity)
        self._schreier_sims()
        
    def __contains__(self, key):
        return self.identity == self._membership_siftee(key, self.schreier_graphs, self.base)
    
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
                    if cand * (h ^ -1) in H:
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
                    if cand * (h ^ -1) in H:
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
    
    def _schreier_graph(self, num, edges = None):
        if edges is None:
            edges = self.generators
        edges_inv = [g**-1 for g in edges]
        schreier_graph = [None for _ in range(len(self.identity))]
        schreier_graph[num - 1] = self.identity
        return self._schreier_graph_expand(schreier_graph, edges, 0)
    
    def _schreier_graph_expand(self, schreier_graph, edges, new_edge_index):
        edges_inv = [g**-1 for g in edges]
        old_frontier = [i + 1 for i, g in enumerate(schreier_graph) if g is not None]
        new_frontier = []
        cur_index = 0
        for num in old_frontier:
            for g, g_inv in zip(edges[new_edge_index:], edges_inv[new_edge_index:]):
                image = num**g_inv                    
                if schreier_graph[image - 1] is None:
                    schreier_graph[image - 1] = g
                    new_frontier.append(image)    
        while len(new_frontier) > 0:
            cur_num = new_frontier.pop()
            for g, g_inv in zip(edges, edges_inv):
                image = cur_num**g_inv
                if schreier_graph[image - 1] is None:
                    schreier_graph[image - 1] = g
                    new_frontier.append(image)
        return schreier_graph    
    
    def _coset_rep_inverses(self, schreier_graph):
        coset_reps = [None for _ in schreier_graph]
        coset_reps[schreier_graph.index(self.identity)] = self.identity
        for index in [i for i, v in enumerate(schreier_graph) if v is not None]:
            indices_to_coset = [index] #the path back to the identity.
            while coset_reps[indices_to_coset[-1]] is None:
                cur_index = indices_to_coset[-1]
                cur_g = schreier_graph[cur_index]
                cur_num = (cur_index + 1)
                image = cur_num**cur_g
                image_index = image - 1
                indices_to_coset.append(image_index)
            prev_index = indices_to_coset.pop()
            while len(indices_to_coset) > 0:
                cur_index = indices_to_coset.pop()
                coset_reps[cur_index] = schreier_graph[cur_index] * coset_reps[prev_index]
                prev_index = cur_index
        return coset_reps    
    
    def _coset_reps(self, schreier_graph):
        coset_reps = []
        inv = self._coset_rep_inverses(schreier_graph)
        for g in inv:
            if g is not None:
                coset_reps.append(g**-1)
            else:
                coset_reps.append(None)
        return coset_reps
    
    def _coset_rep_inverse(self, image, schreier_graph):
        g = self.identity
        cur_index = image - 1
        cur_num = image
        cur_g = schreier_graph[cur_index]
        while cur_g is not None and cur_g != self.identity:
            g = g * cur_g
            image = cur_num**cur_g                    
            cur_index = image - 1
            cur_num = image
            cur_g = schreier_graph[cur_index]
        if cur_g is None:
            return None
        return g
    
    def _schreier_generators(self, num, coset_reps, edges = None):
        if edges is None:
            edges = self.generators
        schreier_gens = []
        unique_check = {self.identity}
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
    
    def _membership_siftee(self, candidate, schreier_graphs, base = None):
        if base is None:
            base = self.base
        for num, schreier_graph in zip(base, schreier_graphs):
            image = num**candidate
            #We used to construct all coset inverses this is bad we only need one.
            #image_index = image - 1
            #coset_inverses = self._coset_rep_inverses(schreier_graph)
            #coset_rep = coset_inverses[image_index]
            coset_rep = self._coset_rep_inverse(image, schreier_graph)
            if coset_rep is None:
                return candidate
            else:
                candidate = candidate * coset_rep
        return candidate
    
    def _schreier_sims(self):
        chain_generators = [self.generators]
        chain_schreier_generators = [None]
        schreier_graphs = [None]
        gen = chain_generators[0][0]
        first_non_fixed = next(num for num in range(1, len(self.identity) + 1) if num**gen != num)
        base = [first_non_fixed]
        level = 0
        while level > -1:
            schreier_gens = chain_schreier_generators[level]
            if schreier_gens is None: #first time at this level
                num = base[level]
                schreier_graph = schreier_graphs[level]
                gens = chain_generators[level]
                #unnecciary? if schreier_graph is None: #populate for first time
                schreier_graph = self._schreier_graph(num, gens)
                schreier_graphs[level] = schreier_graph
                coset_reps = self._coset_reps(schreier_graph)
                # need in reverse order as they will be popped off.
                schreier_gens = list(reversed(self._schreier_generators(num, coset_reps, gens)))
                chain_schreier_generators[level] = schreier_gens
                
                chain_generators.append([]) #make next level.
                chain_schreier_generators.append(None)
                schreier_graphs.append([])
            
            elif len(schreier_gens) == 0: #have previously exhausted this level
                num = base[level]
                schreier_graph = schreier_graphs[level]
                gens = chain_generators[level]
                self._schreier_graph_expand(schreier_graph, gens, len(gens) - 1)
                coset_reps = self._coset_reps(schreier_graph)
                schreier_gens = list(reversed(self._schreier_generators(num, coset_reps, gens[-1:])))
                chain_schreier_generators[level] = schreier_gens
            
            membership_pass = True #have we passed all membership tests?            
            
            while membership_pass and len(schreier_gens) > 0:
                gen = schreier_gens.pop()
                schreier_graphs_membership = schreier_graphs[level+1:]
                base_membership = base[level+1:] 
                siftee = self._membership_siftee(gen, schreier_graphs_membership, base_membership)
                if siftee != self.identity:
                    membership_pass = False
                    chain_generators[level+1].append(siftee)
                    if len(base) == level + 1: #also need to add to base.
                        first_non_fixed = next(num for num in range(1, len(self.identity) + 1) if num**siftee != num)
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
                    
        self.base = base
        self.chain_generators = chain_generators
        self.schreier_graphs = schreier_graphs
        
        return base, strong_gens, chain_generators, schreier_graphs
    
    def _rand_element(self):
        pass
        

def test_coset_construction_from_schreier_tree(group):
    G = group
    base, strong_gens, chain_generators, schreier_graphs = G._schreier_sims()
    no_errors = True
    for s_g in schreier_graphs[0:-1]:
        coset_inverses_1 = G._coset_rep_inverses(s_g)
        coset_inverses_2 = [G._coset_rep_inverse(i + 1, s_g) for i in range(len(G.identity))]
        if coset_inverses_1 != coset_inverses_2:
            no_errors = False
            print(coset_inverses_1)
            print(coset_inverses_2)
    if no_errors:
        print("pass")
    else:
        print("fail")
        
def test_contains(group, subgroup):
    G = group
    H = subgroup
    G_ele = G._list_elements()
    H_ele = H._list_elements()
    for g in G_ele:
        if not g in G:
            print(g)
        if g in H_ele and g not in H:
            print(g)
        if g in H and g not in H_ele:
            print(g)
    
def test1():
    s1 = Permutation.read_cycle_form([[2,3]], 4)
    s2 = Permutation.read_cycle_form([[1,2,4]], 4)
    G = PermGroup([s1, s2])
    s_g = G._schreier_graph(2)
    print(s_g)
    cosets = G._coset_reps(s_g)
    print(cosets)
    s_gen = G._schreier_generators(2, cosets)
    print(s_gen)
    cand = s_gen[0]
    siftee = G._membership_siftee(cand, [], [])
    print(siftee)    

def test2():
    a = Permutation([1,2,3,4])
    b = Permutation([3,2,1,4])
    G = PermGroup([a])    
    print(G._coset_rep_inverses([a,None,b,None]))
    

def test3():
    s1 = Permutation.read_cycle_form([[2,3,5,7],[9, 10]], 10)
    s2 = Permutation.read_cycle_form([[1,2,4,8],[9, 10]], 10)
    G = PermGroup([s1, s2])
    base, strong_gens, chain_generators, schreier_graphs = G._schreier_sims()
    print(base)
    for b, gen in zip(['_']+base, chain_generators):
        print(b, gen) 

def test4():
    s1 = Permutation.read_cycle_form([[1,2,3,4]], 4)
    s2 = Permutation.read_cycle_form([[1,2]], 4)
    G = PermGroup([s1, s2])
    print(len(G._list_elements()))
    G._print_elements()
    
def test5():
    g1 = Permutation.read_cycle_form([[1,2,3,4]], 4)
    g2 = Permutation.read_cycle_form([[1,2]], 4)
    h1 = Permutation.read_cycle_form([[1,2,3]], 4)
    h2 = Permutation.read_cycle_form([[1,2]], 4)
    G = PermGroup([g1, g2])
    print(len(G._list_elements()))
    G._print_elements()
    H = PermGroup([h1, h2])
    print(len(H._list_elements()))
    H._print_elements()
    print(H*g1)
    print(g1*H)

def test6():    
    s1 = Permutation.read_cycle_form([[2,3,5,7]], 8)
    s2 = Permutation.read_cycle_form([[1,2,4,8]], 8)
    G = PermGroup([s1, s2])
    test_coset_construction_from_schreier_tree(G)

def test7():
    g1 = Permutation.read_cycle_form([[1,2,3,4,5,6,7]], 7)
    g2 = Permutation.read_cycle_form([[1,2]], 7)
    h1 = Permutation.read_cycle_form([[3,4,5,6,7]], 7)
    h2 = Permutation.read_cycle_form([[3,4]], 7)
    G = PermGroup([g1, g2])
    H = PermGroup([h1, h2])
    test_contains(G, H)

def test7():
    g1 = Permutation.read_cycle_form([[1,2,3,4]], 4)
    g2 = Permutation.read_cycle_form([[1,2]], 4)
    h1 = Permutation.read_cycle_form([[1,2,3]], 4)
    h2 = Permutation.read_cycle_form([[1,2]], 4)
    G = PermGroup([g1, g2])
    H = PermGroup([h1, h2])
    cosets = G._left_cosets(H)
    for coset in cosets:
        print(coset._list_elements())
    cosets = G._right_cosets(H)
    for coset in cosets:
        print(coset._list_elements())
    
def main():
    #test_coset_construction_from_schreier_tree()
    #test1()
    #test2()
    #test3()
    test7()
    
    
if __name__ == "__main__":
    main()