def traditional_backtrack_subgroup(group_property, refinement_family, size):
    pbw = PartitionBacktrackWorkhorse(group_property.check, refinement_family, size)
    return pbw.find_partition_backtrack_subgroup()

class TraditionalBacktrackWorkhorse():
    def __init__(self, prop_check, refinement_family, size):
        self.size = size
        self.refinement_family = refinement_family
        self.prop_check = prop_check
        self.left = Partition([0]*size,[-1]*size)
        self.right = Partition([0]*size,[-1]*size)
        self.functions = None
        self.extention_indices = None
        self.function_index = 0        
    
    def find_partition_backtrack_subgroup(self):
        generators = []
        self.functions = self.preprocess()
        self.extention_indices = [0] * len(self.functions)
        
        while self.function_index > 0:
            #Alternative 3-4
            self.extend_right()
    
            #Alternatice 1: premature rule out.
            if self.alt1():
                self.backtrack()
            
            #Alternative 2: discrete check.
            elif self.right.discrete():
                perm = Permutation.read_partitions(left[func_index], right[func_index])
                if not perm.trivial() and self.prop_check(perm):
                    generators.append(perm)
                self.backtrack()

        return generators
    
    
    def find_partition_backtrack_coset(self):
        pass
    
    def backtrack():
        while self.function_index > 0:
            self.right.pop()
            if self.extention_indices[self.function_index] > 0:
                break
            self.function_index -= 1
           
    def alt1():
        #Size violation
        if len(self.right) != self.function_index + 1:
            return True
        elif len(self.right[-1][-1]) != len(left[self.function_index][-1]):
            return True
        #Contained group violation.
        #Minimal in double coset violation.
        #Property dependant violation.
        return False
    
    def extend_right(self):
        index = self.function_index
        special, func = self.functions[index]
        if special:
            split_index = func
            cell = self.right[-1][split_index]
            split_val = cell[self.extention_indices[index]]
            self.right.extend(split_index, [split_val])
            self.extention_indices[index] = (self.extention_indices[index] + 1) % len(cell)
        else:
            func(None, self.right)
        self.function_index += 1
    
    def preprocess(self):
        func_list = []
        while not stack.discrete():
            _,_,func = self.refinement_family.extend(self.left, None)
            while func is not None:
                func_list.append((False, func))
                _,_,func = self.refinement_family.extend(self.left, None)
            if not stack.discrete():
                #this is a special level.
                split_index = self.split_cell(self.left)
                func_list.append(True, split_index)
        return func_list
    
    def split_cell(self, stack):
        top = stack[-1]
        _, index = max([(len(cell),index) for index, cell in enumerate(top)])
        split_cell = [min(top[index])]
        stack.extend(index, split_cell)
        return index