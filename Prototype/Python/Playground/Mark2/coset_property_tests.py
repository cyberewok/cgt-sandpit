import unittest
from group import PermGroup
from partition import Partition
from permutation import Permutation
from coset_property import CosetPropertyUnion
from coset_property import IdentityProperty
from coset_property import PartitionStabaliserProperty
from coset_property import PermutationCommuterProperty
from coset_property import SubgroupProperty

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
        G= PermGroup(gens)
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
        G= PermGroup(gens)
        prop1 = SubgroupProperty(G)
        prop2 = PartitionStabaliserProperty(Partition([[2,3],[1,4]]))
        co_prop = CosetPropertyUnion([prop1,prop2])
        pos = cf([[2,3],[1,4]])
        self.assertTrue(co_prop.property_check(pos))
        
        

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCosetProperty))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())