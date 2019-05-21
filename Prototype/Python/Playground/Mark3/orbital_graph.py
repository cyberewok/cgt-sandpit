from group import PermGroup

class OrbitalGraph():
    def __init__(self, group, pair):
        self.num_vertices = len(group.identity)
        self.edges = sorted(self._pair_orbit(group, pair))
        self.ad_list = [[y for x,y in self.edges if x == v] for v in range(1, self.num_vertices + 1)]
        
        
    def _pair_orbit(self, group, seed_pair):
        act = lambda x, g: (x[0]**g, x[1]**g)
        gens = group.generators
        frontier = [seed_pair]
        orb = set(frontier)
        while len(frontier) > 0:
            next_frontier = []
            for gen in gens:
                for pair in frontier:
                    cand = act(pair, gen)
                    if cand not in orb:
                        orb.add(cand)
                        next_frontier.append(cand)
            frontier = next_frontier
        return list(orb)