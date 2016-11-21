from leon_modifier import LeonModifier

class LeonLogger(LeonModifier):
    pass

class LeonLoggerUnion(LeonLogger):
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
        
class NodePrinter(LeonLogger):
    def exclude_backtrack_index(self, left, right, tree, height, *args):
        print("{}({}): {} -> {}".format(height, len(right) -1, left[height], right[-1]))
    
    def leaf_pass_backtrack_index(self, left, right, tree, *args):
        print("pass")
    
    def leaf_fail_backtrack_index(self, left, right, tree, *args):
        print("fail")