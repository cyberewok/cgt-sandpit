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
    
    def transversal(num, S = generators):
        len
        for s in S:
            num**s