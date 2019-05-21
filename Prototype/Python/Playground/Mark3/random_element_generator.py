from permutation import Permutation
from group import PermGroup
from random import randrange
from math import log2

_DEFAULT_SEED = 961748941

def initialise_random_seed(seed = None):
    if seed is not None:
        set_random_seed(seed)
    else:
        set_random_seed(_DEFAULT_SEED)

def set_random_seed(seed):
    return random.seed()

class RandomGenerator():
    
    def element(self):
        NotImplemented
    
    def add(self):
        NotImplemented
    
class UniformGenerator(RandomGenerator):
    def __init__(self, seed_gens):
        self.G = PermGroup(seed_gens)
        
    def add(self, ele):
        NotImplemented
    
    def element(self):
        return self.G._rand_element()

class ProductReplacer(RandomGenerator):
    def __init__(self, seed_gens, vec_size = None, blanks = None):
        self.seed_gens = [gen for gen in seed_gens]
        self.degree = len(self.seed_gens[0])
        if vec_size is None:
            vec_size = log2(self.degree)*2
        if blanks is None:
            blanks = 30*len(self.seed_gens)
        self.rand = lambda : randrange(len(seed_gens))
        self.rand_deg = lambda : randrange(1, self.degree)        
        while len(self.seed_gens) < vec_size:
            self.seed_gens.append(self.seed_gens[self.rand()]**self.rand_deg())
        self.initialise(blanks)
    
    def initialise(self, num_rolls):
        for _ in range(num_rolls):
            self.element()
    
#    def add(self, ele):
#        self.seed_gens.append(ele)
    
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