from permutation import Permutation
from group import PermGroup
from ordering import ordering_to_key
from random import randrange
from math import log2
from random_element_generator import ProductReplacer
from schreier_structure import DirectSchreierStructure, GraphSchreierStructure

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
        self.level_sifts = []
        self.depth = 0
        self.structure = GraphSchreierStructure(self.degree)
        
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
            
            if self.sift_till_level(cand, level, trails = trials):
                passes += 1
            else:
                ret = False
                passes = 0
                if self.group_order is not None and self.structure.order() == self.group_order:
                    return ret
        return ret
        
    def sift_till_level(self, cand, level, start_level = 0, trails = 0):

        ret = True
        for cur_level in range(start_level, level):
            if cur_level == self.depth:
                self.add_level(cand)
            
            if self.level_sifts[cur_level] < trails:
                if self.structure.extend_level(cand, cur_level):
                    self.level_sifts[cur_level] = 0
                    return False
                else:
                    self.level_sifts[cur_level] += 1
                    ret = False
            
            siftee = self.structure.sift_on_level(cand, cur_level)
            
            if siftee is None:
                self.level_sifts[cur_level] = 0
                self.structure.extend_level(cand, cur_level)
                return False
            
            if siftee.trivial():
                return ret
            
            cand = siftee
        
        return ret

    def add_level(self, cand):
        self.level_sifts.append(0)
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

class RandomSchreierGeneratorSuperShallow():
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
        self.structure = GraphSchreierStructure(self.degree)
        
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
        self.structure = GraphSchreierStructure(self.degree)
    
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