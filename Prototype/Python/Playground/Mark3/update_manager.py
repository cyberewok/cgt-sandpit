

#want to eventually use this as the new updates manager which keeps track
#splits made to the stack.
class UpdatesManager():
    def __init__(self, stack):
        self.degree = stack.degree
        self.num_ops = 0
        self.extensions = [cell for cell in stack[-1]]
        self.crit_ops = [-1] * len(stack)
        self.stack = stack
    
    def __len__(self):
        return len(self.crit_ops)
    
    def single_add(self, split_index, split_val):
        self.stack.extend(split_index, [split_val])
        self.num_ops += 1        
        self.extensions.append([split_val])        
        self.crit_ops.append(self.num_ops)
        
        if _asserts: assert(len(self.crit_ops) == len(self.stack))
        if _asserts: assert(len(self.extensions) == len(self.crit_ops)) 
    
    def multi_add(self,func):
        stack = self.stack        
        ret = stack.multi_extend(func)
        if ret:
            self.num_ops += 1        
            changes = stack.report_changes(len(self.extensions))
            self.extensions.extend(changes)        
            self.crit_ops.extend([self.num_ops] *len(changes))

        if _asserts: assert(len(self.extensions) == len(self.stack))   
        if _asserts: assert(len(self.extensions) == len(self.crit_ops))        
        return ret
    
    def multi_remove(self):
        stack = self.stack
        self.num_ops += 1
        while len(self.crit_ops) > len(stack):
            self.extensions.pop()
            self.crit_ops.pop()
        if _asserts: assert(len(self.crit_ops) == len(self.stack))  
        if _asserts: assert(len(self.extensions) == len(self.crit_ops))       
    
    def _bin_search(self, op_id):
        lo = 0
        hi = len(self.crit_ops)
        #lo<=des<hi
        while lo < hi - 1:
            mid = (hi + lo)//2
            if self.crit_ops[mid] <= op_id:
                lo = mid
            else:
                hi = mid
                
        #if len(self.crit_ops) == 0 or self.crit_ops[0] < lo:
            #lo = None
            
        return lo
    
    def last_pop_height(self, op_id):
        #now returning the height of the stack that is the top most unchanged
        return self._bin_search(op_id) + 1
    
    def report_changes(self, prev_op = None, last_pop = None):
        #last pop given as a stack height.
        if prev_op is None:
            prev_op = 0
        if last_pop is None:
            last_pop = self._bin_search(prev_op) + 1
        #should be a generator.
        #all the new ones
        return self.extensions[last_pop:], self.num_ops
    
    def fix_info(self, level = 0):
        return self.stack.fix_info(level)
    
    def fix(self):
        return self.stack.fix()
    
    def special_values(self):
        pass
    
    def special_levels(self):
        pass