import unittest
from leon_search import PartitionBacktrackWorkhorse as PBW
from permutation import Permutation
from partition import Partition
from refinement import Refinement, SubgroupFamily, PartitionStabaliserFamily, IdentityFamily
from coset_property import CosetProperty, SubgroupProperty, PartitionStabaliserProperty, IdentityProperty
from group import PermGroup

class TestLeonSearch(unittest.TestCase):
    def test_r_base(self):
        cf = Permutation.read_cycle_form
        a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
        b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
        fam_subgroup = SubgroupFamily(PermGroup([a,b])) 
        
        stab = Partition([[1,3,5,7,9,11],[2,4,6,8,10,12,13]])
        fam_part_stab = PartitionStabaliserFamily(stab)        
        size = 13
        
        fam = Refinement([fam_subgroup, fam_part_stab])
        pbw = PBW(None, fam, size)
        r_base = pbw._r_base()
        lookup = pbw._special_lookup
        special_levels = sorted(list(lookup.keys()))
        special_cells = [lookup[level][0] for level in special_levels]
        special_vals = [lookup[level][1] for level in special_levels]
        
        self.assertTrue(pbw.left.discrete())
        self.assertEqual(special_levels, [1,2,4])
        self.assertEqual(special_cells, [1,1,1])
        self.assertEqual(special_vals, [1,3,5])
        f = pbw.left.fix()
        b = fam_subgroup._group.base
        self.assertEqual(f[:len(b)], b)
    
    def test_tree_traversal(self):
        fam = Refinement([IdentityFamily()])
        prop = CosetProperty([IdentityProperty()])
        pbw = PBW(prop, fam, 4)
        pbw.printing = True
        gens = pbw.find_partition_backtrack_subgroup()
        self.assertEqual(PermGroup(gens).order(), 24)
        print(gens)
    
    def test_partition_backtrack_subgroup_one_prop_subgroup(self):
        cf = Permutation.read_cycle_form
        a = cf([[1,2,3]], 5)
        b = cf([[1,2],[3,4]], 5)
        G = PermGroup([a,b])
        fam_subgroup = SubgroupFamily(G)
        prop_subgroup = SubgroupProperty(G)
        
        fam = Refinement([fam_subgroup])
        prop = CosetProperty([prop_subgroup])
        pbw = PBW(prop, fam, 5)
        
        gens = pbw.find_partition_backtrack_subgroup()
        
        found = []
        s5 = PermGroup([cf([[1,2]],5),cf([[1,2,3,4,5]],5)])
        for ele in s5._list_elements():
            if prop.check(ele):
                found.append(ele)

        self.assertEqual(len(PermGroup(gens)), len(found))
        
    def test_partition_backtrack_subgroup_one_prop_stab(self):
        cf = Permutation.read_cycle_form
        stab = Partition([[1,3,5],[2,4,6]])
        fam_part_stab = PartitionStabaliserFamily(stab)        
        prop_part_stab = PartitionStabaliserProperty(stab)
        
        size = 6
        fam = Refinement([fam_part_stab])
        prop = CosetProperty([prop_part_stab])
        pbw = PBW(prop, fam, size)     
        
        gens = pbw.find_partition_backtrack_subgroup()
        
        found = []
        s6 = PermGroup([cf([[1,2]],6),cf([[1,2,3,4,5,6]],6)])
        for ele in s6._list_elements():
            if prop.check(ele):
                found.append(ele)

        self.assertEqual(len(PermGroup(gens)), len(found))
    
    def test_partition_backtrack_subgroup_two_prop_subgroup_stab(self):        
        cf = Permutation.read_cycle_form
        a = cf([[3,2,6]], 7)
        b = cf([[3,2],[6,7]], 7)
        G = PermGroup([a,b])
        fam_subgroup = SubgroupFamily(G)
        prop_subgroup = SubgroupProperty(G)
        stab = Partition([[1,3,5,7],[2,4,6]])
        fam_part_stab = PartitionStabaliserFamily(stab)        
        prop_part_stab = PartitionStabaliserProperty(stab)
        
        size = 7
        fam = Refinement([fam_part_stab, fam_subgroup])
        prop = CosetProperty([prop_part_stab, prop_subgroup])
        pbw = PBW(prop, fam, size)
        
        gens = pbw.find_partition_backtrack_subgroup()
        
        found = []
        s7 = PermGroup([cf([[1,2]],7),cf([[1,2,3,4,5,6,7]],7)])
        for ele in s7._list_elements():
            if prop.check(ele):
                found.append(ele)

        self.assertEqual(len(PermGroup(gens)), len(found))     
        
    def test_partition_backtrack_subgroup_leon_paper(self):
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
        
        gens = pbw.find_partition_backtrack_subgroup()
        cand_G = PermGroup(gens)
        leon_gens = []
        leon_gens.append(cf([[2,12],[4,10],[5,7],[6,8]],13))
        leon_gens.append(cf([[2,8],[3,5],[4,6],[10,12]],13))
        leon_gens.append(cf([[1,9],[2,4],[6,8],[10,12]],13))
        leon_G = PermGroup(leon_gens)
        third_source = []
        for ele in G._list_elements():
            if prop.check(ele):
                third_source.append(ele)
        self.assertEqual(cand_G.order(), leon_G.order())
        for perm in leon_gens:
            self.assertTrue(perm in G)
            self.assertTrue(perm in cand_G)
        
        

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLeonSearch))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())