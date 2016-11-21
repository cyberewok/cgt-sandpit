class CosetProperty():
    def __init__(self, properties):
        self.props = properties
    
    def check(self, perm):
        for prop in self.props:
            if not prop.check(perm):
                return False
        return True

class IdentityProperty():
    def __init__(self):
        pass
    
    def check(self, perm):
        return True

class SubgroupProperty():
    def __init__(self, group):
        self.group = group
    
    def check(self, perm):
        return perm in self.group
    
class PartitionStabaliserProperty():
    def __init__(self, partition):
        self.partition = partition
    
    def check(self, perm):    
        return self.partition**perm == self.partition

class PermutationCommuterProperty():
    def __init__(self, perm):
        self.perm = perm
    
    def check(self, comm):
        return self.perm * comm == comm * self.perm