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
            schreier_graph[num] = self.identity
        frontier = [i for i in schreier_graph if i is not None]
        cur_index = 0
        while len(frontier) > cur_index:
            cur_num = frontier[cur_index]
            for g in edges:
                g_inv = g**-1
                image = cur_num**g_inv
                if schreier_graph[image] is None:
                    schreier_graph[image] = g
                    frontier.append(image)
            cur_index += 1
        return schreier_graph

def main():
    s1 = Permutation
    G = PermGroup()
    
if __name__ == "__main__":
    main()