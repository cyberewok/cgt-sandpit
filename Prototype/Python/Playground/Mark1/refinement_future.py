from group import PermGroup as Group
from partition import PartitionStack

class RefinementFamily():
    def extension_functions(self, left):
        pass

class Refinement(RefinementFamily):
    def __init__(self, refinement_families):
        self.families = refinement_families
    
    def extention_functions(self, left):
        for family in self.families:
            funcs = family.extention_functions(left)
            if funcs is not None:
                return funcs
        return None

class IdentityFamily(RefinementFamily):
    pass

#Highly unoptimised used for testing.
class SubgroupFamily(RefinementFamily):
    def __init__(self, group, key = None):
        self._key_single = key
        self._key_orbit = (lambda x: key(x[0])) if key is not None else None
        self._group = group

    def find_element(self,pre, post):
        if pre == post:
            return self._group.identity
        else:
            return self._group.prefix_postfix_image_member(pre, post)
    
    def full_extention(self,left, right, base_stack, i, orbit):
        
        for stack in (left, right):
            if stack is not None and i<len(stack[-1]):
                pre = base_stack.fix()
                post = stack.fix()
                rep = self.find_element(pre, post)
                if rep is not None:
                    orbit = [ele**rep for ele in orbit]                
                    stack.extend(i, orbit)
        return left, right
    
    def extension_functions(self,left):
        base = left.fix()
        self._group.change_base(base)
        orbits = self._group.orbits(len(base), key = self._key_single)
        orbits.sort(key = self._key_orbit)
        left_copy = PartitionStack.deep_copy(left)
        for i in range(left.base_size):
            for orbit in orbits:
                before = len(stack)
                self.full_extention(left, right,base_stack,i,orbit)
                if len(stack) > before:
                    func = lambda l=None, r=None : self.full_extention(l,r,base_stack,i,orbit)
                    func._info = [self.__class__,base, i,orbit ]
                    return left, right, func
        return left, right, None   
    

#Highly unoptimised used just for tests:
class PartitionStabaliserFamily(RefinementFamily):
    def __init__(self, partition):
        self.partition = partition
    
    def full_extention(self, left, right, i, j):
        for stack in (left, right):
            if stack is not None and i<len(stack[-1]) and j<len(self.partition):
                stack.extend(i, self.partition[j])
        return left, right
    
    def extend(self,left, right):
        stack = right if left is None else left
        for i in range(stack.base_size):
            for j in range(len(self.partition)):
                before = len(stack)
                left, right = self.full_extention(left, right,i,j)
                if len(stack) > before:
                    func = lambda l=None, r=None : self.full_extention(l,r,i,j)
                    func._info = [self.__class__,i,j]
                    return left, right, func
        return left, right, None