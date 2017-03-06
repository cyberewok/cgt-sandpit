import sys

def schreier_sims0():
    from permutation import Permutation
    from refinement import SubgroupFamily, PartitionStabaliserFamily, Refinement
    from partition import Partition
    from group import PermGroup
    from leon_search import PartitionBacktrackWorkhorse as PBW
    from coset_property import CosetProperty, SubgroupProperty, PartitionStabaliserProperty
        
    cf = Permutation.read_cycle_form
    a = cf([[1,2]], 4)
    b = cf([[1,2,3,4]], 4)
    G = PermGroup.fixed_base_group([a,b],[1,2,3,4])
    base = G.base
    graphs = G.schreier_graphs
    gens = G.chain_generators
    print("Base is: {}".format(base))
    for i in range(len(graphs)):
        print("Generators and schreier graph for G[{}]:".format(i + 1))
        print(gens[i])
        print(graphs[i])    

def leon_trivial1():
    from permutation import Permutation
    from refinement import SubgroupFamily, PartitionStabaliserFamily, Refinement
    from partition import Partition
    from group import PermGroup
    from leon_search import PartitionBacktrackWorkhorse as PBW
    from coset_property import CosetProperty, SubgroupProperty, PartitionStabaliserProperty
        
    cf = Permutation.read_cycle_form
    a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
    b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
    G = PermGroup([a,b])
    fam_subgroup = SubgroupFamily(G)
    prop_subgroup = SubgroupProperty(G)
    
    stab = Partition([[1,2],[3,4]])
    fam_part_stab = PartitionStabaliserFamily(stab)        
    prop_part_stab = PartitionStabaliserProperty(stab)
    
    size = 4
    fam = Refinement([])
    prop = CosetProperty([prop_part_stab])
    pbw = PBW(prop, fam, size) 
    pbw.printing = True 
    pbw.multi_backtrack = False
    
    print("Refinements: None")
    print("Desired property: partition stabaliser of [[1,2],[3,4]]")
    print("Search space: Sym(4)")
    gens = pbw.find_partition_backtrack_subgroup()
    print("Generators found:")
    for gen in gens:
        print(gen)
        
def leon_trivial2():
    from permutation import Permutation
    from refinement import SubgroupFamily, PartitionStabaliserFamily, Refinement
    from partition import Partition
    from group import PermGroup
    from leon_search import PartitionBacktrackWorkhorse as PBW
    from coset_property import CosetProperty, SubgroupProperty, PartitionStabaliserProperty
        
    cf = Permutation.read_cycle_form
    a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
    b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
    G = PermGroup([a,b])
    fam_subgroup = SubgroupFamily(G)
    prop_subgroup = SubgroupProperty(G)
    
    stab = Partition([[1,2],[3,4]])
    fam_part_stab = PartitionStabaliserFamily(stab)        
    prop_part_stab = PartitionStabaliserProperty(stab)
    
    size = 4
    fam = Refinement([])
    prop = CosetProperty([prop_part_stab])
    pbw = PBW(prop, fam, size) 
    pbw.printing = True 
    pbw.multi_backtrack = True
    
    print("Refinements: None")
    print("Desired property: partition stabaliser of [[1,2],[3,4]]")
    print("Heuristics: multi-backtrack")
    print("Search space: Sym(4)")
    gens = pbw.find_partition_backtrack_subgroup()
    print("Generators found:")
    for gen in gens:
        print(gen)

def leon_trivial3():
    from permutation import Permutation
    from refinement import SubgroupFamily, PartitionStabaliserFamily, Refinement
    from partition import Partition
    from group import PermGroup
    from leon_search import PartitionBacktrackWorkhorse as PBW
    from coset_property import CosetProperty, SubgroupProperty, PartitionStabaliserProperty
        
    cf = Permutation.read_cycle_form
    a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
    b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
    G = PermGroup([a,b])
    fam_subgroup = SubgroupFamily(G)
    prop_subgroup = SubgroupProperty(G)
    
    stab = Partition([[1,2],[3,4]])
    fam_part_stab = PartitionStabaliserFamily(stab)        
    prop_part_stab = PartitionStabaliserProperty(stab)
    
    size = 4
    fam = Refinement([fam_part_stab])
    prop = CosetProperty([prop_part_stab])
    pbw = PBW(prop, fam, size) 
    pbw.printing = True
    pbw.multi_backtrack = False
    pbw.double_coset_check = False
    
    
    print("Refinements: partition stabaliser refinement")
    print("Desired property: partition stabaliser of [[1,2],[3,4]]")
    print("Heuristics: None")
    print("Search space: Sym(4)")
    
    gens = pbw.find_partition_backtrack_subgroup()
    print("Generators found:")
    for gen in gens:
        print(gen)    

def leon_trivial4():
    from permutation import Permutation
    from refinement import SubgroupFamily, PartitionStabaliserFamily, Refinement
    from partition import Partition
    from group import PermGroup
    from leon_search import PartitionBacktrackWorkhorse as PBW
    from coset_property import CosetProperty, SubgroupProperty, PartitionStabaliserProperty
        
    cf = Permutation.read_cycle_form
    a = cf([[1,2,3]], 4)
    b = cf([[2,3,4]], 4)
    G = PermGroup([a,b])
    fam_subgroup = SubgroupFamily(G)
    prop_subgroup = SubgroupProperty(G)
    
    stab = Partition([[1,2],[3,4]])
    fam_part_stab = PartitionStabaliserFamily(stab)        
    prop_part_stab = PartitionStabaliserProperty(stab)
    
    size = 4
    fam = Refinement([fam_subgroup])
    prop = CosetProperty([prop_subgroup, prop_part_stab])
    pbw = PBW(prop, fam, size) 
    pbw.printing = True
    pbw.multi_backtrack = True
    pbw.double_coset_check = False
    
    print("Refinements: subgroup refinement")
    print("Desired property: partition stabaliser of [[1,2],[3,4]] and subgroup of alt(3)")
    print("Heuristics: multi-backtrack")
    print("Search space: Sym(4)")
    
    gens = pbw.find_partition_backtrack_subgroup()
    print("Generators found:")
    for gen in gens:
        print(gen)
        

def leon_trivial5():
    from permutation import Permutation
    from refinement import SubgroupFamily, PartitionStabaliserFamily, Refinement
    from partition import Partition
    from group import PermGroup
    from leon_search import PartitionBacktrackWorkhorse as PBW
    from coset_property import CosetProperty, SubgroupProperty, PartitionStabaliserProperty
        
    cf = Permutation.read_cycle_form
    a = cf([[1,2,3]], 4)
    b = cf([[2,3,4]], 4)
    G = PermGroup([a,b])
    fam_subgroup = SubgroupFamily(G)
    prop_subgroup = SubgroupProperty(G)
    
    stab = Partition([[1,2],[3,4]])
    fam_part_stab = PartitionStabaliserFamily(stab)        
    prop_part_stab = PartitionStabaliserProperty(stab)
    
    size = 4
    fam = Refinement([fam_subgroup, fam_part_stab])
    prop = CosetProperty([prop_subgroup, prop_part_stab])#[prop_part_stab])
    pbw = PBW(prop, fam, size) 
    pbw.printing = True
    pbw.multi_backtrack = True
    pbw.double_coset_check = False
    
    print("Refinements: partition stabaliser refinement and subgroup refinement")
    print("Desired property: partition stabaliser of [[1,2],[3,4]] and subgroup of alt(3)")
    print("Heuristics: multi-backtrack")
    print("Search space: Sym(4)")
    
    gens = pbw.find_partition_backtrack_subgroup()
    print("Generators found:")
    for gen in gens:
        print(gen)    

def leon_trivial55():
    from permutation import Permutation
    from refinement import SubgroupFamily, PartitionStabaliserFamily, Refinement
    from partition import Partition
    from group import PermGroup
    from leon_search import PartitionBacktrackWorkhorse as PBW
    from coset_property import CosetProperty, SubgroupProperty, PartitionStabaliserProperty
        
    cf = Permutation.read_cycle_form
    a = cf([[1,2,3]], 4)
    b = cf([[2,3,4]], 4)
    G = PermGroup([a,b])
    fam_subgroup = SubgroupFamily(G)
    prop_subgroup = SubgroupProperty(G)
    
    stab = Partition([[1,2],[3,4]])
    fam_part_stab = PartitionStabaliserFamily(stab)        
    prop_part_stab = PartitionStabaliserProperty(stab)
    
    size = 4
    fam = Refinement([fam_subgroup, fam_part_stab])
    prop = CosetProperty([prop_subgroup, prop_part_stab])#[prop_part_stab])
    pbw = PBW(prop, fam, size) 
    pbw.printing = True
    pbw.multi_backtrack = True
    pbw.double_coset_check = False
    
    print("Refinements: partition stabaliser refinement and subgroup refinement")
    print("Desired property: partition stabaliser of [[1,2],[3,4]] and subgroup of alt(3)")
    print("Heuristics: multi-backtrack")
    print("Search space: Sym(4)")
    
    gens = pbw.find_partition_backtrack_subgroup()
    print("Generators found:")
    for gen in gens:
        print(gen)

def leon_rbase6():
    from permutation import Permutation
    from refinement import SubgroupFamily, PartitionStabaliserFamily, Refinement
    from partition import Partition
    from group import PermGroup
    from leon_search import PartitionBacktrackWorkhorse as PBW
        
    cf = Permutation.read_cycle_form
    a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
    b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
    fam_subgroup = SubgroupFamily(PermGroup([a,b])) 
    
    stab = Partition([[1,3,5,7,9,11],[2,4,6,8,10,12,13]])
    fam_part_stab = PartitionStabaliserFamily(stab)        
    size = 13
    
    print("Refinements: partition stabaliser refinement and subgroup refinement")
    print("Desired property: partition stabaliser of [[1,3,5,7,9,11],[2,4,6,8,10,12,13]] and subgroup of <[[2,3],[4,6],[5,8],[9,11]], [[1,2,4,7,9,3,5,6,8,10,11,12,13]]>")
    print("Heuristics: multi-backtrack")
    print("Search space: Sym(13)")
    
    fam = Refinement([fam_subgroup, fam_part_stab])
    pbw = PBW(None, fam, size)
    pbw.printing = True
    r_base = pbw._r_base()
    lookup = pbw._special_lookup
    special_levels = sorted(list(lookup.keys()))    

def leon_full7():
    from permutation import Permutation
    from refinement import SubgroupFamily, PartitionStabaliserFamily, Refinement
    from partition import Partition
    from group import PermGroup
    from leon_search import PartitionBacktrackWorkhorse as PBW
    from coset_property import CosetProperty, SubgroupProperty, PartitionStabaliserProperty
        
    cf = Permutation.read_cycle_form
    a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
    b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
    G = PermGroup([a,b])
    fam_subgroup = SubgroupFamily(G)
    prop_subgroup = SubgroupProperty(G)
    
    stab = Partition([[1,3,5,7,9,11],[2,4,6,8,10,12,13]])
    fam_part_stab = PartitionStabaliserFamily(stab)        
    prop_part_stab = PartitionStabaliserProperty(stab)
    
    size = 13
    fam = Refinement([fam_subgroup, fam_part_stab])
    prop = CosetProperty([prop_subgroup, prop_part_stab])
    pbw = PBW(prop, fam, size) 
    pbw.printing = True    
    
    print("Refinements: partition stabaliser refinement and subgroup refinement")
    print("Desired property: partition stabaliser of [[1,3,5,7,9,11],[2,4,6,8,10,12,13]] and subgroup of <[[2,3],[4,6],[5,8],[9,11]], [[1,2,4,7,9,3,5,6,8,10,11,12,13]]>")
    print("Heuristics: multi-backtrack")
    print("Search space: Sym(13)")
    
    gens = pbw.find_partition_backtrack_subgroup()
    print("Generators found:")
    for gen in gens:
        print(gen)
    



if __name__ == '__main__':
    from _example_path_tools import add_path_examples
    add_path_examples()
    prev_out = sys.stdout
    
    sys.stdout = open("0classic.txt", "w")
    schreier_sims0()    
    sys.stdout = open("1noRnoH.txt", "w") 
    leon_trivial1()
    sys.stdout = open("2noRH.txt", "w")
    leon_trivial2()
    sys.stdout = open("3RnoH.txt", "w") 
    leon_trivial3()
    sys.stdout = open("4RsubgroupH.txt", "w") 
    leon_trivial4() 
    sys.stdout = open("5bothRH.txt", "w") 
    leon_trivial5()
    sys.stdout = open("5bothRH2.txt", "w")   
    leon_trivial55()             
    sys.stdout = open("6LeonRbase.txt", "w")
    leon_rbase6()
    sys.stdout = open("7LeonFull.txt", "w")    
    leon_full7()
    
    sys.stdout = prev_out