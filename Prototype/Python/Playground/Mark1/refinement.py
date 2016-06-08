class Refinement():
    def __init__(self, extention_functions):
        self.extentions = extention_functions
    
    def extend(self, left_stack = None, right_stack = None):
        for extention in self.extentions:
            left_extend, right_extend, func = extention(left_stack, right_stack)
            if func is not None:
                return left_extend, right_extend, func
        return left_stack, right_stack, None

def _identity():
    def extend(left, right):
        return left, right, None
    return extend

#Highly unoptimised used just for tests:
def partition_stabaliser(partition):  
    def full_extention(left, right, i, j):
        for stack in (left, right):
            if stack is not None and i<len(stack[-1]) and j<len(partition):
                stack.extend(i, partition[j])
        return left, right
    
    def extend(left, right):
        stack = right if left is None else left
        for i in range(stack.base_size):
            for j in range(len(partition)):
                before = len(stack)
                left, right = full_extention(left, right,i,j)
                if len(stack) > before:
                    func = lambda l=None, r=None : full_extention(l,r,i,j)
                    return left, right, func
        return left, right, None
    
    return extend