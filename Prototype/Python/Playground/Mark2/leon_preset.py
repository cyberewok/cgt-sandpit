from refinement import RefinementUnion, SubgroupFamily
from leon_modifier import ModifierUnion, PartitionStackConstraint, MultiBacktracker
from refinement import UnorderedPartitionStabaliserFamily
from refinement import NormaliserFamily, IdentityFamily
from coset_property import CosetPropertyUnion, SubgroupProperty
from coset_property import NormaliserProperty, IdentityProperty
from leon_search import LeonSearch
from group import PermGroup

def subgroup_search(set_up_mods, size):    
    con = PartitionStackConstraint()
    multi_back = MultiBacktracker()
    mods = ModifierUnion([set_up_mods, con, multi_back])
    ls = LeonSearch(mods, size)
    
    gens = ls.subgroup_generators()
    return gens
    

def symmetric_group(degree):
    size = degree
    
    fam_norm = IdentityFamily()        
    prop_norm = IdentityProperty()
    
    fam = RefinementUnion([fam_norm])
    prop = CosetPropertyUnion([prop_norm])
    
    mods = ModifierUnion([fam, prop])

    gens = subgroup_search(mods, size)

    ret = PermGroup(gens)
    return ret

def symmetric_normaliser(group, extra_mods = None):
    if extra_mods is None:
        extra_mods = []
        
    size = group.degree
    
    fam_norm = NormaliserFamily(group)        
    prop_norm = NormaliserProperty(group)
    
    fam = RefinementUnion([fam_norm])
    prop = CosetPropertyUnion([prop_norm])
    
    mods = ModifierUnion(extra_mods + [fam, prop])

    gens = subgroup_search(mods, size)

    norm_G = PermGroup(gens)
    return norm_G