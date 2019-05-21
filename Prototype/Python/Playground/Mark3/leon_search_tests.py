import unittest
from leon_search import LeonSearch
from permutation import Permutation
from partition import Partition
from leon_modifier import ModifierUnion, PartitionStackConstraint, MultiBacktracker
from refinement import RefinementUnion, SubgroupFamily, PartitionStabaliserFamily, IdentityFamily
from refinement import UnorderedPartitionStabaliserFamily, PartitionImageFamily
from coset_property import CosetPropertyUnion, SubgroupProperty, PartitionStabaliserProperty, IdentityProperty
from coset_property import UnorderedPartitionStabaliserProperty, PartitionImageProperty
from leon_logger import LeonLoggerUnion, NodeCounter, NodePrinter
from group import PermGroup

class TestLeonSearch(unittest.TestCase):
    def test_r_base(self):
        cf = Permutation.read_cycle_form
        a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
        b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
        fam_subgroup = SubgroupFamily(PermGroup.fixed_base_group([a,b])) 
        
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
        b = fam_subgroup._group.schreier_structure.base_till_level()
        self.assertEqual(f[:len(b)], b)
    
    def test_tree_traversal(self):
        fam = RefinementUnion([IdentityFamily()])
        prop = CosetPropertyUnion([IdentityProperty()])
        mods = ModifierUnion([fam, prop])     
        ls = LeonSearch(mods, 4)
        gens = ls.subgroup_generators()
        self.assertEqual(PermGroup.fixed_base_group(gens).order(), 24)
    
    def test_partition_backtrack_subgroup_one_prop_subgroup(self):
        cf = Permutation.read_cycle_form
        a = cf([[1,2,3]], 5)
        b = cf([[1,2],[3,4]], 5)
        G = PermGroup.fixed_base_group([a,b])
        fam_subgroup = SubgroupFamily(G)
        prop_subgroup = SubgroupProperty(G)
        
        fam = RefinementUnion([fam_subgroup])
        prop = CosetPropertyUnion([prop_subgroup])
        con = PartitionStackConstraint()
        mods = ModifierUnion([fam, prop, con])
        
        ls = LeonSearch(mods, 5)
        
        gens = ls.subgroup_generators()
        
        found = []
        s5 = PermGroup.fixed_base_group([cf([[1,2]],5),cf([[1,2,3,4,5]],5)])
        for ele in s5._list_elements():
            if prop.property_check(ele):
                found.append(ele)

        self.assertEqual(sorted(PermGroup.fixed_base_group(gens)._list_elements()), sorted(found))
        
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
        
        gens = ls.subgroup_generators()
        
        found = []
        s6 = PermGroup.fixed_base_group([cf([[1,2]],6),cf([[1,2,3,4,5,6]],6)])
        for ele in s6._list_elements():
            if prop.property_check(ele):
                found.append(ele)

        self.assertEqual(sorted(PermGroup.fixed_base_group(gens)._list_elements()), sorted(found))
    
    def test_partition_backtrack_subgroup_two_prop_subgroup_stab(self):        
        cf = Permutation.read_cycle_form
        a = cf([[3,2,6]], 7)
        b = cf([[3,2],[6,7]], 7)
        G = PermGroup.fixed_base_group([a,b])
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
        
        gens = ls.subgroup_generators()
        
        found = []
        s7 = PermGroup.fixed_base_group([cf([[1,2]],7),cf([[1,2,3,4,5,6,7]],7)])
        for ele in s7._list_elements():
            if prop.property_check(ele):
                found.append(ele)

        self.assertEqual(len(PermGroup.fixed_base_group(gens)), len(found))     
        
    def test_partition_backtrack_subgroup_leon_paper(self):
        cf = Permutation.read_cycle_form
        a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
        b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
        G = PermGroup.fixed_base_group([a,b])
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
        
        gens = ls.subgroup_generators()
        cand_G = PermGroup.fixed_base_group(gens)
        leon_gens = []
        leon_gens.append(cf([[2,12],[4,10],[5,7],[6,8]],13))
        leon_gens.append(cf([[2,8],[3,5],[4,6],[10,12]],13))
        leon_gens.append(cf([[1,9],[2,4],[6,8],[10,12]],13))
        leon_G = PermGroup.fixed_base_group(leon_gens)
        third_source = []
        for ele in G._list_elements():
            if prop.property_check(ele):
                third_source.append(ele)
        self.assertEqual(cand_G.order(), leon_G.order())
        for perm in leon_gens:
            self.assertTrue(perm in G)
            self.assertTrue(perm in cand_G)
    
    def test_unordered_partition_stabaliser_leon_paper(self):
        size = 21
        cf  = lambda x:Permutation.read_cycle_form(x,size)
        a = cf([[1,3,9,16,18,19,13],[2,12,11,17,20,10,14],[4,5,6,21,7,8,15]])
        b = cf([[2,3],[4,12],[5,7],[8,10],[13,14]])
        G = PermGroup.fixed_base_group([a,b])
        self.assertEqual(len(G),5040)
        fam_sub = SubgroupFamily(G)
        prop_sub = SubgroupProperty(G)
        
        stab = Partition([[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18],[19,20,21]])
        fam_stab = UnorderedPartitionStabaliserFamily(stab)
        prop_stab = UnorderedPartitionStabaliserProperty(stab)
        
        fam = ModifierUnion([fam_sub,fam_stab])
        prop = ModifierUnion([prop_sub,prop_stab])
        con = PartitionStackConstraint()
        multi_back = MultiBacktracker()
        mods = ModifierUnion([fam, prop, con, multi_back])
        ls = LeonSearch(mods, size)
        
        G_stab = PermGroup.fixed_base_group(ls.subgroup_generators())
        self.assertEqual(len(G_stab), 36)
        
        
    def test_multi_backtrack(self):
        cf = Permutation.read_cycle_form
        a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
        b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
        G = PermGroup.fixed_base_group([a,b])
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
        gens1 = ls.subgroup_generators()
        count2 = NodeCounter()       
        mods = ModifierUnion([fam, prop, con, count2])
        ls = LeonSearch(mods, size)
        gens2 = ls.subgroup_generators()
        self.assertTrue(count1.node_count < count2.node_count)
        self.assertEqual(PermGroup.fixed_base_group(gens1).order(), PermGroup.fixed_base_group(gens2).order())
        
    def test_partition_image(self):
        cf = Permutation.read_cycle_form
        part = Partition([[1,3,5],[2,4,6]])
        image = Partition([[2,3,5],[1,4,6]])
        fam_part_image = PartitionImageFamily(part, image)        
        prop_part_image = PartitionImageProperty(part, image)
        
        size = 6
        fam = RefinementUnion([fam_part_image])
        prop = CosetPropertyUnion([prop_part_image])
        con = PartitionStackConstraint()
        mods = ModifierUnion([fam, prop, con])
        ls = LeonSearch(mods, size)
        
        coset_rep = ls.coset_representative()
        self.assertTrue(prop.property_check(coset_rep))   
    
    def test_partition_image_from_subgroup(self):
        size = 8
        cf = lambda x: Permutation.read_cycle_form(x, size)
        
        a = cf([[1,2,3,4,5,6,7]])
        b = cf([[6,7,8]])
        G = PermGroup.fixed_base_group([a,b])
        fam_subgroup = SubgroupFamily(G)
        prop_subgroup = SubgroupProperty(G)  
        
        part = Partition([[1,3],[5,7],[2,4,6,8]])
        image = Partition([[8,4],[5,1],[2,3,6,7]])
        fam_part_image = PartitionImageFamily(part, image)        
        prop_part_image = PartitionImageProperty(part, image)
        
        fam = RefinementUnion([fam_part_image,fam_subgroup])
        prop = CosetPropertyUnion([prop_part_image, prop_subgroup])
        con = PartitionStackConstraint()
        mods = ModifierUnion([fam, prop, con])
        ls = LeonSearch(mods, size)
        
        coset_rep = ls.coset_representative()
        self.assertTrue(prop.property_check(coset_rep))
    
    def test_subgroup_conjugacy(self):
        return
        size = 8
        cf = lambda x: Permutation.read_cycle_form(x, size)
        
        a = cf([[1,2,3,4,5]])
        b = cf([[4,5,6]])
        c = cf([[1,2,4,6,7]])
        d = cf([[6,7,8]])
        G1 = PermGroup.fixed_base_group([a,b])
        G2 = PermGroup.fixed_base_group([c,d])
        
        fam_conj = PartitionImageFamily(part, image)        
        prop_conj = SungroupConjugacyProperty(part, image)
        
        fam = RefinementUnion([fam_part_image,fam_subgroup])
        prop = CosetPropertyUnion([prop_part_image, prop_subgroup])
        con = PartitionStackConstraint()
        mods = ModifierUnion([fam, prop, con])
        ls = LeonSearch(mods, size)
        
        coset_rep = ls.coset_representative()
        self.assertTrue(prop.property_check(coset_rep))       

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLeonSearch))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())