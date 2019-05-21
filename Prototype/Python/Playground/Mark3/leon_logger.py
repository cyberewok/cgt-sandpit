from leon_modifier import LeonModifier, ModifierUnion

class LeonLogger(LeonModifier):
    pass

class LeonLoggerUnion(LeonModifier):
    #Depreciated. Use LeonModifierUnion instead.
    def __init__(self, loggers):
        self.loggers = loggers
        
    def call_all(self, func_value):
        for logger in self.loggers:
            func_value(logger)
    
    def extension_functions(self, left, *args):
        func_value = lambda mod: mod.extension_functions(left, *args)
        self.call_all(func_value)
    
    def exclude_backtrack_index(self, left, right, tree, *args):
        func_value = lambda mod: mod.exclude_backtrack_index(left, right, tree, *args)        
        self.call_all(func_value)
    
    def leaf_pass_backtrack_index(self, left, right, tree, *args):
        func_value = lambda mod: mod.leaf_pass_backtrack_index(left, right, tree, *args)        
        self.call_all(func_value)
    
    def leaf_fail_backtrack_index(self, left, right, tree, *args):
        func_value = lambda mod: mod.leaf_fail_backtrack_index(left, right, tree, *args)        
        self.call_all(func_value)   


class NodeCounter(LeonLogger):
    def __init__(self):
        self.leaf_count = 0
        self.pos_leaf_count = 0
        self.node_count = 0
        
    def exclude_backtrack_index(self, left, right, tree, *args):
        self.node_count += 1
    
    def leaf_pass_backtrack_index(self, left, right, tree, *args):
        self.leaf_count += 1        
        self.pos_leaf_count += 1
    
    def leaf_fail_backtrack_index(self, left, right, tree, *args):
        self.leaf_count += 1
        
    def __str__(self):
        ret = "NodeCounter object:\n"
        
        ret += "  Total nodes visited: {}\n".format(self.node_count)
        ret += "  Total nummber of leaves: {}\n".format(self.leaf_count)        
        ret += "  Number of positive leaves: {}\n".format(self.pos_leaf_count)        
        
        return ret
        
class NodePrinter(LeonLogger):
    def exclude_backtrack_index(self, left, right, tree, top_index, *args):
        print("{}({}): {} -> {}".format(top_index, len(right) -1, left[top_index], right[-1]))
    
    def leaf_pass_backtrack_index(self, left, right, tree, *args):
        print("pass")
    
    def leaf_fail_backtrack_index(self, left, right, tree, *args):
        print("fail")
        
    def extension_functions(self, left, *args):
        print("{}: {} (preprocessing)".format(len(left) -1, left[-1]))