from partition import PartitionStack
from permutation import Permutation
from position_tracker import PositionTracker
from group import PermGroup
import ordering

def partition_backtrack_subgroup(modifier_family, size):
    ls = LeonSearch(modifier_family, size)
    return PermGroup(ls.subgroup())

class LeonSearch():
    def __init__(self, leon_modifiers, degree):
        self.degree = degree
        self.tree_modifiers = leon_modifiers
        self.left = None
        self.right = None
        self._left_split_index = None
        self._cur_height = None        
        self._r_base = None
        self._special_level_sizes = None
        #Tree position tracker to store traversal information.
        self._cur_position = None
        #Dictionary with heights as keys and split index and point pairs as values.
        self._special_lookup = None
    
    def initialise_partition_stacks(self):
        size = self.degree
        self.left = PartitionStack([0]*size,[-1]*size)
        self.right = PartitionStack([0]*size,[-1]*size)
    
    def initialise_r_base(self):
        self.tree_modifiers.begin_preprocessing()
        r_base = []
        special_cell_sizes = []
        special_lookup = dict()
        top_index = 0
        while top_index < self.degree -1:
            funcs = self.tree_modifiers.extension_functions(self.left)
            if funcs is not None:
                left_func, right_func = funcs
                left_func(self.left)
                r_base.append(right_func)                
                special_cell_sizes.append(0)
            else:
                r_base.append(None)
                cell, cell_size, point = self._split_left_cell()
                special_cell_sizes.append(cell_size)
                special_lookup[top_index] = (cell, point)   
            top_index += 1
            self.tree_modifiers.height_increase(self.left, None, None, top_index)            
        self._r_base = r_base
        self._special_level_sizes = special_cell_sizes
        self._special_lookup = special_lookup
        self.tree_modifiers.end_preprocessing()        
    
    def initialise_search_tree(self):
        self._cur_height = 0
        self._cur_position = PositionTracker(self._special_level_sizes)        
        
    def subgroup_generators(self):   
        #Needs to be done in this order.
        self.initialise_partition_stacks()
        self.initialise_r_base()
        self.initialise_search_tree()
                        
        gens = []
        

        self.tree_modifiers.begin_search()             
        while self._cur_height > -1:
            #alt_1 rule out.
            backtrack_index = self.tree_modifiers.exclude_backtrack_index(self.left, self.right, self._cur_position, self._cur_height)
            if backtrack_index is not None:
                self.backtrack(backtrack_index)
            
            #alt_2 discrete check.
            elif self.right.discrete():
                perm = Permutation.read_partitions(self.left[self._cur_height], self.right[self._cur_height])            
                if not perm.trivial() and self.tree_modifiers.property_check(perm):
                    gens.append(perm)
                    backtrack_index = self.tree_modifiers.leaf_pass_backtrack_index(self.left,self.right,self._cur_position)            
                else:
                    backtrack_index = self.tree_modifiers.leaf_fail_backtrack_index(self.left,self.right,self._cur_position)
                self.backtrack(backtrack_index)
            
            #alt_3 function to extend.
            elif self._r_base[self._cur_height] is not None:
                func = self._r_base[self._cur_height]
                func(self.right)
                self._cur_height += 1
                self.tree_modifiers.height_increase(self.left, self.right, self._cur_position, self._cur_height)  
            
            #alt_4 special level.    
            else:
                self._extend_right()
        
        self.tree_modifiers.end_search()         
        return gens
    
    def backtrack(self, new_height = None):
        if new_height is None:
            new_height = self._cur_height
        self._cur_height = self._cur_position.increment(new_height)    
        if self._cur_height > -1:
            while len(self.right) > self._cur_height + 1:
                self.right.pop()
            self.tree_modifiers.height_decrease(self.left, self.right, self._cur_position, self._cur_height)
            self._extend_right()

    def _extend_right(self):
        index = self._cur_height
        split_index, _ = self._special_lookup[index]
        cell = self.right[index][split_index]
        try:    
            split_val = cell[self._cur_position[index]]            
        except IndexError:
            for i in range(index + 1):
                a = self._cur_position
                b = self.right[i]
                c = self.left[i]
                print("\n{} -> {}\n{}".format(c,b,a))
            #this is where it screws
            # if this invoked it is likely that backtracking is not going high enough.
            raise IndexError("DIFFERENT")
        self.right.extend(split_index, [split_val])
        self._cur_height += 1
        self.tree_modifiers.height_increase(self.left, self.right, self._cur_position, self._cur_height)  
        
    def _split_left_cell(self):
        #Overwrite this with a clever function that queries the refinements for
        #clues as to which cell and element to split.
        top = self.left[-1]
        if self._left_split_index is None or len(top[self._left_split_index]) < 2:
            _, self._left_split_index = min([(len(cell),index) for index, cell in enumerate(top) if len(cell) > 1])
        cell = top[self._left_split_index]
        point = cell[0]
        cell_size = len(cell)
        #Turn checks off.
        self.left.extend(self._left_split_index, [point])
        return self._left_split_index, cell_size, point

class PartitionBacktrackWorkhorse():
    def __init__(self, group_property, refinement_family, size):
        self.size = size
        self.refinement_family = refinement_family
        self.group_property = group_property
        self.left = PartitionStack([0]*size,[-1]*size)
        self.right = PartitionStack([0]*size,[-1]*size)
        self._cur_height = 0
        self._cur_position = None
        self._special_lookup = None
        self._left_split_index = None
        self.printing = False
        self.multi_backtrack = True
        self.double_coset_check = False
    
    def find_partition_backtrack_subgroup(self):
        #Assume the refinement families are symmetric.
        generators = []
        r_base = self._r_base()
        count = 0
        leaf_count = 0
        

        if self.printing:
            print("-----------------------------------")
            print("Traversing tree:")
        
        while self._cur_height > -1:
            count += 1
            if self.printing:
                a = self._cur_position
                b = self.right[self._cur_height]
                c = self.left[self._cur_height]
                
                print("\n{}: {}\n{} -> {}".format(self._cur_height,a,c,b)) 
            #Alternatice 1: premature rule out.
            if self.alt1():
                if self.printing:
                    print("Alternative 1: partition violation")
                #print("alt_1")
                self.backtrack(self._cur_height - 1)
            
            #Alternative 2: discrete check.
            elif self.right.discrete():
                leaf_count += 1
                #print("alt_2")
                perm = Permutation.read_partitions(self.left[self._cur_height], self.right[self._cur_height])
                if self.double_coset_check and self.printing:
                    G=PermGroup(generators)
                    Dco = G*perm*G
                    perm_key = ordering.ordering_to_perm_key(self.left.fix())
                    if Dco.mid_minimal(key = perm_key):
                        print("Actually minimal in own double coset: {}".format(Dco._list_elements(Perm_key)))
                    
                added = False                
                if not perm.trivial() and self.group_property.check(perm):
                    generators.append(perm)
                    added = True
                    #self.backtrack()
                if self.printing:
                    print("Alternative 2 found permutation: {} ({})".format(perm, added))
                if self.multi_backtrack and added:
                    self.backtrack(self._cur_position.min_changed_index())
                else:
                    self.backtrack()
            
            #Alternative 3: not a special level
            elif r_base[self._cur_height] is not None:
                #print("alt_3")
                r_base[self._cur_height](None, self.right)
                if self.printing:
                    print("Alternative 3 applying function: {}".format(r_base[self._cur_height]._info))  
                self._cur_height += 1                
            
            #Alternative 4: is a special level
            else:
                if self.printing:
                    print("Alternative 4 special level")                  
                #print("alt_4")
                self.extend_right()
        
        if self.printing:
            print("\nFinished tree traversal.")
            print("Visited {} vertices ({} of which were terminal).".format(count, leaf_count))

        return generators
    
    def _r_base(self):
        if self.printing:
            print("Constructing r-base:")
        r_base = []
        special_cell_sizes = []
        special_lookup = dict()
        height = 0
        while height < self.size -1:
            if self.printing:
                print("\n{}".format(self.left[-1]))
            _,_,func = self.refinement_family.extend(self.left, None)
            r_base.append(func)            
            if func is not None:
                if self.printing:
                    print(func._info)
                special_cell_sizes.append(0)
            else:
                if self.printing:
                    print("Special level:")
                cell, cell_size, point = self._split_left_cell()
                special_cell_sizes.append(cell_size)
                special_lookup[height] = (cell, point)
            height += 1
        if self.printing:
            print("\n{}".format(self.left[-1]))      
        self._cur_position = PositionTracker(special_cell_sizes)
        self._special_lookup = special_lookup
        if self.printing:
            print("\nFinished R-base construction.")
            _temp_levels = sorted([level for level in special_lookup])
            print("Special levels: {}".format(_temp_levels))
            special_cells = [special_lookup[level][0] for level in _temp_levels]
            special_vals = [special_lookup[level][1] for level in _temp_levels]
            print("Basis of group: {}".format(special_vals))
            print("Ordering from rbase: {}".format(self.left.fix()))            
        return r_base

    def _split_left_cell(self):
        #Overwrite this with a clever function that queries the refinements for
        #clues as to which cell and element to split.
        top = self.left[-1]
        if self._left_split_index is None or len(top[self._left_split_index]) < 2:
            _, self._left_split_index = min([(len(cell),index) for index, cell in enumerate(top) if len(cell) > 1])
        cell = top[self._left_split_index]
        point = cell[0]
        cell_size = len(cell)
        #Turn checks off.
        self.left.extend(self._left_split_index, [point])
        return self._left_split_index, cell_size, point
    
    def find_partition_backtrack_coset(self):        
        #Assume the refinement families are LR-symmetric.
        r_base = self._r_base()
        count = 0
        
        while self._cur_height > -1:
            count += 1
            #a = self._cur_position
            #b = self.right[self._cur_height]
            #c = self.left[self._cur_height]
            #if self.size == 13:
            #print("\n{}:{}\n{} -> {}".format(self._cur_height,a,c,b)) 
            #Alternatice 1: premature rule out.
            if self.alt1():
                #print("alt_1")
                self.backtrack(self._cur_height - 1)
            
            #Alternative 2: discrete check.
            elif self.right.discrete():
                #print("alt_2")
                perm = Permutation.read_partitions(self.left[self._cur_height], self.right[self._cur_height])
                if self.group_property.check(perm):
                    return perm
                #self.backtrack()
                self.backtrack(self._cur_position.min_changed_index())
            
            #Alternative 3: not a special level
            elif r_base[self._cur_height] is not None:
                #print("alt_3")
                r_base[self._cur_height](None, self.right)
                self._cur_height += 1
            
            #Alternative 4: is a special level
            else:
                #print("alt_4")
                self.extend_right()
        
        print(count)
        return generators
    
    def backtrack(self, new_height = None):
        if new_height is None:
            new_height = self._cur_height
        self._cur_height = self._cur_position.increment(new_height)    
        if self._cur_height > -1:
            while len(self.right) > self._cur_height + 1:
                self.right.pop()
            self.extend_right()
        
                  
    def alt1(self):
        #Size violation
        if len(self.right) != self._cur_height + 1:
            return True
        elif len(self.right[-1][-1]) != len(self.left[self._cur_height][-1]):
            return True
        #Contained group violation.
        #Minimal in double coset violation.    
        #Property dependant violation.
        return False
    
    def extend_right(self):
        index = self._cur_height
        split_index, _ = self._special_lookup[index]
        cell = self.right[index][split_index]
        try:    
            split_val = cell[self._cur_position[index]]            
        except IndexError:
            for i in range(index + 1):
                a = self._cur_position
                b = self.right[i]
                c = self.left[i]
                print("\n{} -> {}\n{}".format(c,b,a))
            #this is where it screws
            raise IndexError("DIFFERENT")
        self.right.extend(split_index, [split_val])
        self._cur_height += 1

class PartitionBacktrackWorkhorseOLD():
    def __init__(self, prop_check, refinement_family, size):
        self.size = size
        self.refinement_family = refinement_family
        self.prop_check = prop_check
        self.left = Partition([0]*size,[-1]*size)
        self.right = Partition([0]*size,[-1]*size)
        self.functions = None
        self.extension_indices = None
        self.function_index = 0        
    
    def find_partition_backtrack_subgroup(self):
        #Assume the refinement families are symmetric.
        generators = []
        self.functions = self.preprocess()
        self.extension_indices = [0] * len(self.functions)
        
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
            if self.extension_indices[self.function_index] > 0:
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
            split_val = cell[self.extension_indices[index]]
            self.right.extend(split_index, [split_val])
            self.extension_indices[index] = (self.extension_indices[index] + 1) % len(cell)
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