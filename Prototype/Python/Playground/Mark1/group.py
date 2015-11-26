from permutation import Permutation

class PermGroup():
    def __init__(self, generators = None, base = None):
        if generators is None:
            generators = []
        else:
            self.generators = generators
        if len(generators) == 0:
            self.identity = Permutation([])
        else:
            g = generators[0]
            self.identity = g**-1 * g
        if base is None:
            self.base = []
        else:
            self.base = base
    
    def _schreier_graph(self, num, edges = None, schreier_graph = None):
        if edges is None:
            edges = self.generators
        if schreier_graph is None:    
            schreier_graph = [None for _ in range(len(self.identity))]
            schreier_graph[num - 1] = self.identity
        frontier = [i + 1 for i, g in enumerate(schreier_graph) if g is not None]
        cur_index = 0
        while len(frontier) > cur_index:
            cur_num = frontier[cur_index]
            for g in edges:
                g_inv = g**-1
                image = cur_num**g_inv
                if schreier_graph[image - 1] is None:
                    schreier_graph[image - 1] = g
                    frontier.append(image)
            cur_index += 1
        return schreier_graph
    
    def _coset_reps(self, schreier_graph):
        coset_reps = [None for _ in schreier_graph]
        coset_reps[schreier_graph.index(self.identity)] = self.identity
        for index in range(len(schreier_graph)):
            indices_to_coset = [index]
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
        coset_reps = [g**-1 for g in coset_reps]
        return coset_reps
            
    
    def _schreier_generators(self, num, coset_reps, edges = None):
        if edges is None:
            edges = self.generators
        schreier_gens = []
        unique_check = {self.identity}
        for r in coset_reps:
            for s in edges:
                rs = r * s
                rs_coset_index = (num**rs) - 1
                rs_coset_rep = coset_reps[rs_coset_index]
                gen = rs * rs_coset_rep**-1
                if gen not in unique_check:    
                    schreier_gens.append(gen)
                    unique_check.add(gen)
        return schreier_gens    

def main():
    s1 = Permutation.read_cycle_form([[2,3]], 4)
    s2 = Permutation.read_cycle_form([[1,2,4]], 4)
    G = PermGroup([s1, s2])
    s_g = G._schreier_graph(2)
    print(s_g)
    cosets = G._coset_reps(s_g)
    print(cosets)
    s_gen = G._schreier_generators(2, cosets)
    print(s_gen)
    
if __name__ == "__main__":
    main()