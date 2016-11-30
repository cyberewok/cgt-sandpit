from leon_modifier import LeonModifier, ModifierUnion

class CosetProperty(LeonModifier):
    def property_check(self, perm, *args):
        raise NotImplementedError
    
class CosetPropertyUnion(LeonModifier):
    #Depreciated. Use LeonModifierUnion instead.
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
    
class UnorderedPartitionStabaliserProperty(CosetProperty):
    def __init__(self, partition):
        self.partition = partition
        self.rev_lookup = dict()        
        for index, cell in enumerate(partition):
            for ele in cell:
                self.rev_lookup[ele]=index
                
    
    def property_check(self, perm, *args):
        image = self.partition**perm
        for cell in image:
            first =  cell[0]
            org_index = self.rev_lookup[first]
            if len(cell) != len(self.partition[org_index]):
                return False
            for ele in cell[1:]:
                if self.rev_lookup[ele]!=org_index:
                    return False
        return True
                    
            

class PermutationCommuterProperty(CosetProperty):
    def __init__(self, perm):
        self.perm = perm
    
    def property_check(self, comm, *args):
        return self.perm * comm == comm * self.perm