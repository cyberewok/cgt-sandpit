class CosetProperty():
    def __init__(self, check_functions):
        self.functions = check_functions
    
    def check(self, perm):
        for func in self.functions:
            if not func(perm):
                return False
        return True

def _identity():
    return lambda perm: True
    
def partition_stabaliser(partition):
    return lambda perm: partition**perm == partition