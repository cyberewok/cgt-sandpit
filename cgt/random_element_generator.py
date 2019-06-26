from .permutation import Permutation
from random import randrange
from math import log2

class RandomGenerator():
    
    def element(self):
        NotImplemented
    
    def add(self):
        NotImplemented

class SGSRandomGenerator(RandomGenerator):
    def __init__(self, structure, level=0):
        self.level = level
        self.structure = structure.clone()

    def element(self):
        return self.structure.random_element(level=self.level)

class ProductReplacer(RandomGenerator):
    def __init__(self, seed_gens, vec_size=None, blanks=None):
        self.seed_gens = [gen for gen in seed_gens]
        self.degree = len(self.seed_gens[0])
        if vec_size is None:
            vec_size = log2(self.degree)*2
        if blanks is None:
            blanks = 5*len(self.seed_gens)
        rand_initial = lambda: randrange(len(seed_gens))
        self.rand_deg = lambda: randrange(1, self.degree)
        while len(self.seed_gens) < vec_size:
            self.seed_gens.append(self.seed_gens[rand_initial()]**self.rand_deg())
        self.rand = lambda: randrange(len(self.seed_gens))
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
    #THIS IS NOT TO BE USED FOR STATISTICALLY RANDOM RESULTS.
    def __init__(self, seed_gens):
        self.seed_gens = seed_gens
        self.degree = len(self.seed_gens[0])
        self.identity = Permutation.read_cycle_form([], self.degree)
        self.rand = lambda: randrange(2)
    
    def add(self, ele):
        self.seed_gens.append(ele)
    
    def element(self):
        tot = self.identity
        for gen in self.seed_gens:
            if self.rand():
                tot = tot * gen
        return tot