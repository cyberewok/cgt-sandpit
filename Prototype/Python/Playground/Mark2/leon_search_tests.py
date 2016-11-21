import unittest
from leon_search import LeonSearch
from permutation import Permutation
from partition import Partition
from leon_modifier import ModifierUnion, PartitionStackConstraint, MultiBacktracker
from refinement import RefinementUnion, SubgroupFamily, PartitionStabaliserFamily, IdentityFamily
from coset_property import CosetPropertyUnion, SubgroupProperty, PartitionStabaliserProperty, IdentityProperty
from leon_logger import LeonLoggerUnion, NodeCounter, NodePrinter
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
        
        fam = RefinementUnion([fam_subgroup, fam_part_stab])
        
        fail_con = PartitionStackConstraint()
        tree_mods = ModifierUnion([fail_con])
        
        mods = ModifierUnion([fam, tree_mods])
        
        ls = LeonSearch(mods, size)
        ls.initialise_partition_stacks()
        ls.initialise_r_base()
        lookup = ls._special_lookup
        special_levels = sorted(list(lookup.keys()))
        special_cells = [lookup[level][0] for level in special_levels]
        special_vals = [lookup[level][1] for level in special_levels]
        
        self.assertTrue(ls.left.discrete())
        self.assertEqual(special_levels, [1,2,4])
        self.assertEqual(special_cells, [1,1,1])
        self.assertEqual(special_vals, [1,3,5])
        f = ls.left.fix()
        b = fam_subgroup._group.base
        self.assertEqual(f[:len(b)], b)
    
    def test_tree_traversal(self):
        fam = RefinementUnion([IdentityFamily()])
        prop = CosetPropertyUnion([IdentityProperty()])
        mods = ModifierUnion([fam, prop])     
        ls = LeonSearch(mods, 4)
        gens = ls.subgroup()
        self.assertEqual(PermGroup(gens).order(), 24)
    
    def test_partition_backtrack_subgroup_one_prop_subgroup(self):
        cf = Permutation.read_cycle_form
        a = cf([[1,2,3]], 5)
        b = cf([[1,2],[3,4]], 5)
        G = PermGroup([a,b])
        fam_subgroup = SubgroupFamily(G)
        prop_subgroup = SubgroupProperty(G)
        
        fam = RefinementUnion([fam_subgroup])
        prop = CosetPropertyUnion([prop_subgroup])
        con = PartitionStackConstraint()
        mods = ModifierUnion([fam, prop, con])
        
        ls = LeonSearch(mods, 5)
        
        gens = ls.subgroup()
        
        found = []
        s5 = PermGroup([cf([[1,2]],5),cf([[1,2,3,4,5]],5)])
        for ele in s5._list_elements():
            if prop.property_check(ele):
                found.append(ele)

        self.assertEqual(sorted(PermGroup(gens)._list_elements()), sorted(found))
        
    def test_partition_backtrack_subgroup_one_prop_stab(self):
        cf = Permutation.read_cycle_form
        stab = Partition([[1,3,5],[2,4,6]])
        fam_part_stab = PartitionStabaliserFamily(stab)        
        prop_part_stab = PartitionStabaliserProperty(stab)
        
        size = 6
        fam = RefinementUnion([fam_part_stab])
        prop = CosetPropertyUnion([prop_part_stab])
        con = PartitionStackConstraint()
        mods = ModifierUnion([fam, prop, con])
        ls = LeonSearch(mods, size)
        
        gens = ls.subgroup()
        
        found = []
        s6 = PermGroup([cf([[1,2]],6),cf([[1,2,3,4,5,6]],6)])
        for ele in s6._list_elements():
            if prop.property_check(ele):
                found.append(ele)

        self.assertEqual(sorted(PermGroup(gens)._list_elements()), sorted(found))
    
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
        fam = RefinementUnion([fam_part_stab, fam_subgroup])
        prop = CosetPropertyUnion([prop_part_stab, prop_subgroup])
        con = PartitionStackConstraint()
        mods = ModifierUnion([fam, prop, con])
        ls = LeonSearch(mods, size)
        
        gens = ls.subgroup()
        
        found = []
        s7 = PermGroup([cf([[1,2]],7),cf([[1,2,3,4,5,6,7]],7)])
        for ele in s7._list_elements():
            if prop.property_check(ele):
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
        fam = RefinementUnion([fam_subgroup, fam_part_stab])
        prop = CosetPropertyUnion([prop_subgroup, prop_part_stab])
        con = PartitionStackConstraint()
        multi_back = MultiBacktracker()
        mods = ModifierUnion([fam, prop, con, multi_back])
        ls = LeonSearch(mods, size)
        
        gens = ls.subgroup()
        cand_G = PermGroup(gens)
        leon_gens = []
        leon_gens.append(cf([[2,12],[4,10],[5,7],[6,8]],13))
        leon_gens.append(cf([[2,8],[3,5],[4,6],[10,12]],13))
        leon_gens.append(cf([[1,9],[2,4],[6,8],[10,12]],13))
        leon_G = PermGroup(leon_gens)
        third_source = []
        for ele in G._list_elements():
            if prop.property_check(ele):
                third_source.append(ele)
        self.assertEqual(cand_G.order(), leon_G.order())
        for perm in leon_gens:
            self.assertTrue(perm in G)
            self.assertTrue(perm in cand_G)
            
    def test_multi_backtrack(self):
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
        fam = RefinementUnion([fam_subgroup, fam_part_stab])
        prop = CosetPropertyUnion([prop_subgroup, prop_part_stab])
        con = PartitionStackConstraint()
        count1 = NodeCounter()
        multi_back = MultiBacktracker()
        mods = ModifierUnion([fam, prop, con, multi_back, count1])
        ls = LeonSearch(mods, size)
        gens1 = ls.subgroup()
        count2 = NodeCounter()       
        mods = ModifierUnion([fam, prop, con, count2])
        ls = LeonSearch(mods, size)
        gens2 = ls.subgroup()
        self.assertTrue(count1.node_count < count2.node_count)
        self.assertEqual(PermGroup(gens1).order(), PermGroup(gens2).order())
        
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLeonSearch))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())