from group import PermGroup as Group
from partition import PartitionStack, Partition
from leon_modifier import LeonModifier, ModifierUnion

class Refinement(LeonModifier):
    def extension_functions(self, left,*args):
        raise NotImplementedError

class RefinementUnion(LeonModifier):
    #Depreciated. Use LeonModifierUnion instead.
    def __init__(self, refinement_families):
        self.modifiers = refinement_families
    
    def extension_functions(self, left,*args):
        for family in self.modifiers:
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
    
class UnorderedPartitionStabaliserFamily(Refinement):
    def __init__(self, partition):
        self.partition = partition
        self.degree = len(partition)
        self.top_index = 0
        self.derived = None
        self.derived_indices = None
        self.initialise_derived()
        self.left_derived = None
        self.left_derived_indices = None    

    def begin_preprocessing(self, *args):
        self.initialise_derived()
    
    def end_preprocessing(self, *args):
        self.left_derived = self.derived
        self.left_derived_indices = self.derived_indices        
    
    def begin_search(self, *args):
        self.initialise_derived()
    
    def initialise_derived(self, *args):
        self.derived = PartitionStack([0]*self.degree, [-1]*self.degree)
        self.derived_indices = []
        func = lambda element: len(self.partition[element - 1])
        self.derived.multi_extend(func)
        self.derived_indices.append(len(self.derived) - 1)
        self.top_index = 0
    
    def height_increase(self, left, right, tree, new_top_index, *args):
        if new_top_index != self.top_index + 1:
            raise IndexError("Cannot increase by more than one height. (new: {}, old: {})".format(new_top_index, self.top_index))
        
        stack = left
        if self.left_derived is not None:
            stack = right
            
        if new_top_index != len(stack):
            #Unsynchronised caller
            new_top_index = len(stack) - 1
            
        split_cell = stack[-1,-1]
        def int_func(element):
            count = 0
            cand_cell = self.partition[element - 1]
            for cand in cand_cell:
                cand_index = cand - 1
                if stack._finals[cand_index] == new_top_index:
                    count += 1
            return count
        self.derived.multi_extend(int_func)
        self.derived_indices.append(len(self.derived) - 1)
        self.top_index += 1
        
    def height_decrease(self, left, right, tree, new_top_index, *args):
        if self.top_index <= new_top_index:
            raise IndexError("{} new height larger than {}.".format(new_top_index, self.top_index))
        while self.top_index > new_top_index:
            self.derived_indices.pop()
            limit = self.derived_indices[-1]
            self.top_index -= 1
            self.derived.pop_to_height(limit + 1)
    
    def _full_extension(self, stack, i, j):
        cell_union_indices = self.derived[-1,j]
        cell_union = []
        for ele in cell_union_indices:
            cell_union += self.partition[ele - 1]        
        if stack is not None:
            stack.extend(i, cell_union)
        return stack
    
    def extension_functions(self, left, *args):
        for i in range(len(left)):
            unions = self.derived[-1]
            for j in range(len(unions)):
                cell_union = []
                for ele in unions[j]:
                    cell_union += self.partition[ele - 1]
                if left.can_extend(i, cell_union):
                    func = lambda stack : self._full_extension(stack,i,j)
                    func._info = [self.__class__,i,j]
                    return func, func
        return None

class UnorderedPartitionStabaliserFamilyNew(Refinement):
    def __init__(self, partition):
        self.partition = partition
        self.degree = len(partition)
        self.top_index = 0
        self.derived = None
        self.derived_indices = None
        self.initialise_derived()
        self.left_derived = None
        self.left_derived_indices = None    

    def begin_preprocessing(self, *args):
        self.initialise_derived()
    
    def end_preprocessing(self, *args):
        self.left_derived = self.derived
        self.left_derived_indices = self.derived_indices        
    
    def begin_search(self, *args):
        self.initialise_derived()
    
    def initialise_derived(self, *args):
        self.derived = PartitionStack([0]*self.degree, [-1]*self.degree)
        self.derived_indices = []
        func = lambda element: len(self.partition[element - 1])
        self.derived.multi_extend(func)
        self.derived_indices.append(len(self.derived) - 1)
        self.top_index = 0
    
    def height_increase(self, left, right, tree, new_top_index, *args):
        if new_top_index != self.top_index + 1:
            raise IndexError("Cannot increase by more than one height. (new: {}, old: {})".format(new_top_index, self.top_index))
        
        stack = left
        if self.left_derived is not None:
            stack = right
            
        if new_top_index != len(stack):
            #Unsynchronised caller
            new_top_index = len(stack) - 1
            
        split_cell = stack[-1,-1]
        def int_func(element):
            count = 0
            cand_cell = self.partition[element - 1]
            for cand in cand_cell:
                cand_index = cand - 1
                if stack._finals[cand_index] == new_top_index:
                    count += 1
            return count
        self.derived.multi_extend(int_func)
        self.derived_indices.append(len(self.derived) - 1)
        self.top_index += 1
        
    def height_decrease(self, left, right, tree, new_top_index, *args):
        if self.top_index <= new_top_index:
            raise IndexError("{} new height larger than {}.".format(new_top_index, self.top_index))
        while self.top_index > new_top_index:
            self.derived_indices.pop()
            limit = self.derived_indices[-1]
            self.top_index -= 1
            self.derived.pop_to_height(limit + 1)
    
    def _full_extension(self, stack, i, j):
        cell_union_indices = self.derived[-1,j]
        cell_union = []
        for ele in cell_union_indices:
            cell_union += self.partition[ele - 1]        
        if stack is not None:
            stack.extend(i, cell_union)
        return stack
    
    def extension_functions(self, left, *args):
        for i in range(len(left)):
            unions = self.derived[-1]
            for j in range(len(unions)):
                cell_union = []
                for ele in unions[j]:
                    cell_union += self.partition[ele - 1]
                if left.can_extend(i, cell_union):
                    func = lambda stack : self._full_extension(stack,i,j)
                    func._info = [self.__class__,i,j]
                    return func, func
        return None
    
class NormaliserFamily(Refinement):
    def __init__(self, group):
        self.top_index = 0
        partition = Partition(group.orbits())
        self.sub_families = [UnorderedPartitionStabaliserFamily(partition)]
        self._rbase_phase = False
    
    def begin_preprocessing(self, *args):
        self._rbase_phase = True
        for fam in self.sub_families:
            fam.begin_preprocessing(*args)
        
    def end_preprocessing(self, *args):
        self._rbase_phase = False
        for fam in self.sub_families:
            fam.end_preprocessing(*args)     
    
    def begin_search(self, *args):
        for fam in self.sub_families:
            fam.begin_search(*args)
    
    def height_increase(self, left, right, tree, new_top_index, *args):
        if new_top_index != self.top_index + 1:
            raise IndexError("Can't increase by more than one height. (new: {}, old: {})".format(new_top_index, self.top_index))
        #Check the top index for 
        
        for fam in self.sub_families:
            fam.height_increase(left, right, tree, new_top_index, *args)
        
        self.top_index += 1
    
    def height_decrease(self, left, right, tree, new_top_index, *args):
        if self.top_index <= new_top_index:
            raise IndexError("{} new height larger than {}.".format(new_top_index, self.top_index))
        
        for fam in self.sub_families:
            fam.height_decrease(left, right, tree, new_top_index, *args)
        
        self.top_index = new_top_index
    
    def extension_functions(self, left, *args):
        for fam in self.sub_families:
            cand = fam.extension_functions(left, *args)
            if cand is not None:
                return cand
            
class NormaliserFamilyNEW(Refinement):
    def __init__(self, group):
        self.top_index = 0
        partition = Partition(group.orbits())
        self.sub_families = [UnorderedPartitionStabaliserFamily(partition)]
        self._rbase_phase = False
    
    def begin_preprocessing(self, *args):
        self._rbase_phase = True
        for fam in self.sub_families:
            fam.begin_preprocessing(*args)
        
    def end_preprocessing(self, *args):
        self._rbase_phase = False
        for fam in self.sub_families:
            fam.end_preprocessing(*args)     
    
    def begin_search(self, *args):
        for fam in self.sub_families:
            fam.begin_search(*args)
    
    def height_increase(self, left, right, tree, new_top_index, *args):
        if _rbase_phase:
            self.sub_families.append()
        
        if new_top_index != self.top_index + 1:
            raise IndexError("Can't increase by more than one height. (new: {}, old: {})".format(new_top_index, self.top_index))
        #Check the top index for 
        
        for fam in self.sub_families:
            fam.height_increase(left, right, tree, new_top_index, *args)
        
        self.top_index += 1
    
    def height_decrease(self, left, right, tree, new_top_index, *args):
        if self.top_index <= new_top_index:
            raise IndexError("{} new height larger than {}.".format(new_top_index, self.top_index))
        
        for fam in self.sub_families:
            fam.height_decrease(left, right, tree, new_top_index, *args)
        
        self.top_index = new_top_index
    
    def extension_functions(self, left, *args):
        for fam in self.sub_families:
            cand = fam.extension_functions(left, *args)
            if cand is not None:
                return cand
            
class PartitionImageFamily(Refinement):
    def __init__(self, left_partition, right_partition):
        self.partition = left_partition
        self.image = right_partition
    
    def _full_extension(self, stack, extension, i, j):
        if stack is not None:
            stack.extend(i, extension[j])
        return stack
    
    def extension_functions(self,left,*args):
        for i in range(left.degree):
            for j in range(left.degree):
                if j<len(self.partition) and left.can_extend(i, self.partition[j]):
                    left_func = lambda stack : self._full_extension(stack, self.partition,i,j)
                    right_func = lambda stack : self._full_extension(stack, self.image,i,j)
                    left_func._info = [self.__class__,i,j]
                    right_func._info = [self.__class__,i,j]
                    return left_func, right_func
        return None
    

class UnorderedPartitionImageFamily(Refinement):
    def __init__(self, left_partition, right_partition):
        self.partition = left_partition
        self.image = right_partition
        self.degree = len(partition)
        self.top_index = 0
        self.derived = None
        self.derived_indices = None
        self.initialise_derived()
        self.left_derived = None
        self.left_derived_indices = None    

    def begin_preprocessing(self, *args):
        self.initialise_derived()
    
    def end_preprocessing(self, *args):
        self.left_derived = self.derived
        self.left_derived_indices = self.derived_indices        
    
    def begin_search(self, *args):
        self.initialise_derived()
    
    def initialise_derived(self, *args):
        self.derived = PartitionStack([0]*self.degree, [-1]*self.degree)
        self.derived_indices = []
        func = lambda element: len(self.partition[element - 1])
        self.derived.multi_extend(func)
        self.derived_indices.append(len(self.derived) - 1)
        self.top_index = 0
    
    def height_increase(self, left, right, tree, new_top_index, *args):
        stack = left
        if self.left_derived is not None:
            stack = right
            
        if new_top_index != len(stack):
            #Unsynchronised caller
            new_top_index = len(stack) - 1

        if new_top_index != self.top_index + 1:
            raise IndexError("Cannot increase by more than one height. (new: {}, old: {})".format(new_top_index, self.top_index))        
            
        split_cell = stack[-1,-1]
        def int_func(element):
            count = 0
            cand_cell = self.partition[element - 1]
            for cand in cand_cell:
                cand_index = cand - 1
                if stack._finals[cand_index] == new_top_index:
                    count += 1
            return count
        self.derived.multi_extend(int_func)
        self.derived_indices.append(len(self.derived) - 1)
        self.top_index += 1
        
    def height_decrease(self, left, right, tree, new_top_index, *args):
        if self.top_index <= new_top_index:
            raise IndexError("{} new height larger than {}.".format(new_top_index, self.top_index))
        while self.top_index > new_top_index:
            self.derived_indices.pop()
            limit = self.derived_indices[-1]
            self.top_index -= 1
            self.derived.pop_to_height(limit + 1)
    
    def _full_extension(self, stack, i, j):
        cell_union_indices = self.derived[-1,j]
        cell_union = []
        for ele in cell_union_indices:
            cell_union += self.partition[ele - 1]        
        if stack is not None:
            stack.extend(i, cell_union)
        return stack
    
    def extension_functions(self, left, *args):
        for i in range(len(left)):
            unions = self.derived[-1]
            for j in range(len(unions)):
                cell_union = []
                for ele in unions[j]:
                    cell_union += self.partition[ele - 1]
                if left.can_extend(i, cell_union):
                    func = lambda stack : self._full_extension(stack,i,j)
                    func._info = [self.__class__,i,j]
                    return func, func
        return None