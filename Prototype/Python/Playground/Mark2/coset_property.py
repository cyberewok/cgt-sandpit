from leon_modifier import LeonModifier

class CosetProperty(LeonModifier):
    def property_check(self, perm, *args):
        raise NotImplementedError
    
class CosetPropertyUnion(CosetProperty):
    def __init__(self, properties):
        self.props = properties
    
    def property_check(self, perm, *args):
        for prop in self.props:
            if not prop.property_check(perm, *args):
                return False
        return True

class IdentityProperty(CosetProperty):
    def property_check(self, perm, *args):
        return True

class SubgroupProperty(CosetProperty):
    def __init__(self, group):
        self.group = group
    
    def property_check(self, perm, *args):
        return perm in self.group
    
class PartitionStabaliserProperty(CosetProperty):
    def __init__(self, partition):
        self.partition = partition
    
    def property_check(self, perm, *args):    
        return self.partition**perm == self.partition

class PermutationCommuterProperty(CosetProperty):
    def __init__(self, perm):
        self.perm = perm
    
    def property_check(self, comm, *args):
        return self.perm * comm == comm * self.perm