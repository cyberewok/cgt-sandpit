from partition import PartitionStack
from permutation import Permutation
from position_tracker import DynamicPositionTracker
from group import PermGroup
import ordering

def partition_backtrack_canonical(modifier_family, invariant_function, size):
    cs = CanonicalSearch(modifier_family, invariant_function, size)
    return PermGroup(ls.coset_representative())

class CanonicalSearch():
    def __init__(self, leon_modifiers, invariant_func, degree):
        self.degree = degree
        self.tree_modifiers = leon_modifiers
        self.invariant = invariant_func
        self.stack = None
        self._cur_height = None        
        #Tree position tracker to store traversal information.
        self._cur_position = None

    def initialise_partition_stack(self):
        size = self.degree
        self.stack = PartitionStack([0]*size,[-1]*size)

    def initialise_search_tree(self):
        self._cur_height = 0
        self._cur_position = DynamicPositionTracker()   

    def coset_representative(self):
        ele = self._search()
        return ele
    
    def process_leaf(stack):
        pre = stack[-1]
        image = stack.canonical_form()[-1]
        return Permutation.read_partitions(pre, image)
    
    def _search(self):
        self.initialise_partition_stack()
        self.initialise_search_tree()
        
        self.tree_modifiers.begin_preprocessing()
        self.tree_modifiers.end_preprocessing()
                        
        best_leaf = None
        best_value = None
        

        self.tree_modifiers.begin_search()             
        
        while self._cur_height > -1:
            #Check for discrete.
            if self.stack.discrete():
                cand_leaf = self.process_leaf(stack)
                cand_value = self.invarient(cand_leaf)
                if best_value is None or cand_value > best_value:
                    best_leaf, best_value = cand_leaf, cand_value
                    self.backtrack()
            else:
                #Check for refinement.
                funcs = self.tree_modifiers.extension_function(self.stack)
                if funcs is not None:
                    #Refinement exists.
                    func, _ = funcs
                    func(self.stack)
                    self._cur_position.add_level(1)
                else:
                    #Need to manually split.
                    cell, cell_size = self._split_stack_cell()
                    self._cur_position.add_level(cell_size)
                self._cur_height += 1

        return best
    
    def backtrack(self, new_height = None):
        if new_height is None:
            new_height = self._cur_height
        self._cur_height = self._cur_position.increment(new_height)    
        if self._cur_height > -1:
            while len(self.stack) > self._cur_height + 1:
                self.stack.pop()
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
        
    def _split_stack_cell(self):
        #Overwrite this with a clever function that queries the refinements for
        #clues as to which cell and element to split.
        top = self.stack[-1]
        cell_index, cell = self._select_cell(top)
        point = cell[0]
        self.stack.extend(cell_index, [point])
        return cell_index, len(cell)
    
    def _select_cell(self, part):
        for index, cell in enumerate(part):
            if len(cell) > 1:
                return index, cell