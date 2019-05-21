import unittest
from group import PermGroup
from partition import Partition
from permutation import Permutation
from leon_modifier import ModifierUnion
from coset_property import CosetPropertyUnion
from coset_property import IdentityProperty
from coset_property import PartitionStabaliserProperty
from coset_property import PermutationCommuterProperty
from coset_property import SubgroupProperty
from coset_property import UnorderedPartitionStabaliserProperty
from coset_property import NormaliserProperty
from coset_property import SubgroupConjugacyProperty

class TestCosetProperty(unittest.TestCase):
    def test_coset_property_init(self):
        prop = CosetPropertyUnion([IdentityProperty()])
        self.assertTrue(prop.property_check(Permutation.read_cycle_form([[1,2,3,4]], 5)))
                
    def test_partition_stabaliser_property(self):
        prop = CosetPropertyUnion([PartitionStabaliserProperty(Partition([[1,2],[3,4],[5]]))])
        pos = Permutation.read_cycle_form([[1,2]],5)
        neg = Permutation.read_cycle_form([[1,2],[4,5]],5)
        self.assertTrue(prop.property_check(pos))
        self.assertFalse(prop.property_check(neg))
        
    def test_permutation_commuter_property(self):
        prop = CosetPropertyUnion([PermutationCommuterProperty(Permutation([2,1,3,4]))])
        pos = Permutation.read_cycle_form([[3,4]],4)
        neg = Permutation.read_cycle_form([[2,3]],4)
        self.assertTrue(prop.property_check(pos))
        self.assertFalse(prop.property_check(neg))
    
    def test_subgroup_property(self):
        cf = Permutation.read_cycle_form
        a = cf([[1,2,3]],4)
        b = cf([[1,2],[3,4]],4)
        gens = [a,b]
        G= PermGroup.fixed_base_group(gens)
        prop = CosetPropertyUnion([SubgroupProperty(G)])
        pos = cf([[2,3,4]],4)        
        neg = cf([[3,4]],4)
        self.assertTrue(prop.property_check(pos))
        self.assertFalse(prop.property_check(neg))
    
    def test_multi_coset_property(self):
        cf = Permutation.read_cycle_form
        a = cf([[1,2,3]],4)
        b = cf([[1,2],[3,4]],4)
        gens = [a,b]
        G= PermGroup.fixed_base_group(gens)
        prop1 = SubgroupProperty(G)
        prop2 = PartitionStabaliserProperty(Partition([[2,3],[1,4]]))
        co_prop = CosetPropertyUnion([prop1,prop2])
        pos = cf([[2,3],[1,4]])
        self.assertTrue(co_prop.property_check(pos))
        
    def test_unordered_partition_stabaliser_property(self):
        size = 5
        cf = lambda x:Permutation.read_cycle_form(x,size)
        part = Partition([[1,2],[3,4],[5]])
        prop = ModifierUnion([UnorderedPartitionStabaliserProperty(part)])
        pos = cf([[1,3],[2,4]])
        neg = cf([[1,2],[4,5]])
        self.assertTrue(prop.property_check(pos))
        self.assertFalse(prop.property_check(neg)) 
    
    def naive_normaliser_test(self, G, H):
        #only works for tiny groups watch out.
        prop = ModifierUnion([NormaliserProperty(H)])
        norm = []
        for g in G._list_elements():
            g_inv = g** (-1)
            sat = True
            for h in H._list_elements():
                if g_inv * h * g not in H:
                    sat = False
                    break                   
            if sat:
                norm.append(g)
                self.assertTrue(prop.property_check(g)) 
            else:
                self.assertFalse(prop.property_check(g))
        #print("{} {} {}".format(len(G), len(H), len(norm)))
    
    def test_normaliser_property(self):
        size = 4
        cf = lambda x:Permutation.read_cycle_form(x,size)
        G = PermGroup.fixed_base_group([cf([[1,2]]), cf([[1,2,3,4]])])
        H1 = PermGroup.fixed_base_group([cf([[1,2,3,4]]),cf([[1,2],[3,4]])])
        H2 = PermGroup.fixed_base_group([cf([[1,2,3,4]])])
        H3 = PermGroup.fixed_base_group([cf([[1,2],[3,4]]), cf([[1,3],[2,4]])])
        self.naive_normaliser_test(G, H1)
        self.naive_normaliser_test(G, H2)
        self.naive_normaliser_test(G, H3)
        
    
    def naive_subgroup_conjugacy_test(self, G, H1, H2):
        #only works for tiny groups watch out.
        prop = ModifierUnion([SubgroupConjugacyProperty(H1, H2)])
        norm = []
        for g in G._list_elements():
            g_inv = g** (-1)
            sat = True
            for h in H1._list_elements():
                if g_inv * h * g not in H2:
                    sat = False
                    break                   
            if sat:
                norm.append(g)
                self.assertTrue(prop.property_check(g)) 
            else:
                self.assertFalse(prop.property_check(g))
        #print("{} {} {} {}".format(len(G), len(H1), len(H2), len(norm)))
        #print(norm)
        
    def test_subgroup_conjugacy_property(self):
        size = 4
        cf = lambda x:Permutation.read_cycle_form(x,size)
        G = PermGroup.fixed_base_group([cf([[1,2]]), cf([[1,2,3,4]])])
        left1 = PermGroup.fixed_base_group([cf([[1,2,3,4]]),cf([[1,2],[3,4]])])
        right1 = PermGroup.fixed_base_group([cf([[2,1,3,4]]),cf([[1,2],[3,4]])])
        left2 = PermGroup.fixed_base_group([cf([[1,2,3,4]])])
        right2 = PermGroup.fixed_base_group([cf([[1,4,3,2]])])
        H3 = PermGroup.fixed_base_group([cf([[1,2],[3,4]]),cf([[1,3],[2,4]])])
        self.naive_subgroup_conjugacy_test(G, left1, right1)
        self.naive_subgroup_conjugacy_test(G, left2, right2)
        self.naive_subgroup_conjugacy_test(G, H3, H3)  

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCosetProperty))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())