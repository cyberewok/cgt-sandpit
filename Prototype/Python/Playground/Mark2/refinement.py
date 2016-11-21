from group import PermGroup as Group
from partition import PartitionStack
from leon_modifier import LeonModifier

class Refinement(LeonModifier):
    def extension_functions(self, left,*args):
        raise NotImplementedError

class RefinementUnion(Refinement):
    #Depreciated. Use LeonModifierUnion instead.
    def __init__(self, refinement_families):
        self.families = refinement_families
    
    def extension_functions(self, left,*args):
        for family in self.families:
            funcs = family.extension_functions(left,*args)
            if funcs is not None:
                return funcs
        return None

class IdentityFamily(Refinement):
    def extension_functions(self, left):
        pass

#Highly unoptimised used for testing.
class SubgroupFamily(Refinement):
    def __init__(self, group, key = None):
        self._key_single = key
        self._key_orbit = (lambda x: key(x[0])) if key is not None else None
        self._group = group

    def _find_element(self,pre, post):
        if pre == post:
            return self._group.identity
        else:
            return self._group.prefix_postfix_image_member(pre, post)
    
    def _full_extension(self, stack, base, i, orbit):        
        if stack is not None:
            pre = base
            post = stack.fix()
            rep = self._find_element(pre, post)
            if rep is not None:
                orbit = [ele**rep for ele in orbit]                
                stack.extend(i, orbit)
        return stack
    
    def extension_functions(self,left,*args):
        #Only works for r_base construction or equivelent procedure.
        base = left.fix()
        self._group.change_base(base)
        orbits = self._group.orbits(len(base), key = self._key_single)
        orbits.sort(key = self._key_orbit)
        #should be left.height if we can gaureentee complete part. stack.
        for i in range(left.degree):
            for orbit in orbits:
                if left.can_extend(i, orbit):
                    base_stack = PartitionStack.deep_copy(left)
                    func = lambda stack: self._full_extension(stack,base,i,orbit)
                    func._info = [self.__class__,base, i,orbit]
                    return func, func
        return None

#Highly unoptimised used just for tests:
class PartitionStabaliserFamily(Refinement):
    def __init__(self, partition):
        self.partition = partition
    
    def _full_extension(self, stack, i, j):
        if stack is not None:
            stack.extend(i, self.partition[j])
        return stack
    
    def extension_functions(self,left,*args):
        for i in range(left.degree):
            for j in range(left.degree):
                if j<len(self.partition) and left.can_extend(i, self.partition[j]):
                    func = lambda stack : self._full_extension(stack,i,j)
                    func._info = [self.__class__,i,j]
                    return func, func
        return None