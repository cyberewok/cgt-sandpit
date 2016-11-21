from group import PermGroup as Group
from partition import PartitionStack

class LeonModifier():
    def extension_functions(self, left, *args):
        pass
    
    def exclude_backtrack_index(self, left, right, tree, height, *args):
        pass
    
    def leaf_pass_backtrack_index(self, left, right, tree, *args):
        pass
    
    def leaf_fail_backtrack_index(self, left, right, tree, *args):
        pass
    
    def property_check(self, perm, *args):
        pass

class ModifierUnion(LeonModifier):
    def __init__(self, modifiers):
        self.modifiers = modifiers
        
    def first_non_none(self, func_value):
        for modifier in self.modifiers:
            val = func_value(modifier)
            if val is not None:
                return val
    
    def min_non_none(self, func_value):
        min_val = None
        for modifier in self.modifiers:
            val = func_value(modifier)
            if val is not None:
                if min_val is None or val < min_val:
                    min_val = val
        return min_val
    
    def first_non_none_fail(self, func_value):
        for modifier in self.modifiers:
            val = func_value(modifier)
            if val is not None and val == False:
                return False
        return True
    
    def extension_functions(self, left, *args):
        func_value = lambda mod: mod.extension_functions(left, *args)
        return self.first_non_none(func_value)
    
    def exclude_backtrack_index(self, left, right, tree, height, *args):
        func_value = lambda mod: mod.exclude_backtrack_index(left, right, tree, height, *args)        
        return self.min_non_none(func_value)
    
    def leaf_pass_backtrack_index(self, left, right, tree, *args):
        func_value = lambda mod: mod.leaf_pass_backtrack_index(left, right, tree, *args)        
        return self.min_non_none(func_value)
    
    def leaf_fail_backtrack_index(self, left, right, tree, *args):
        func_value = lambda mod: mod.leaf_fail_backtrack_index(left, right, tree, *args)        
        return self.min_non_none(func_value)
    
    def property_check(self, perm, *args):
        func_value = lambda mod: mod.property_check(perm, *args)        
        return self.first_non_none_fail(func_value)
    
class PartitionStackConstraint(LeonModifier):
    def exclude_backtrack_index(self, left, right, tree, height, *args):
        if len(right) != height + 1:
            #print("height terminate")
            #Not convinced this is correct...
            return height - 1
        elif len(right[height][-1]) != len(left[height][-1]):
            #print("size terminate")
            return height - 1
        #Contained group violation.
        #Minimal in double coset violation.    
        #Property dependant violation.
        
class MultiBacktracker(LeonModifier):
    def leaf_pass_backtrack_index(self, left, right, tree, *args):
        return tree.min_changed_index()
    