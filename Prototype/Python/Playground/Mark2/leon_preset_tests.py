import unittest
from coset_property import NormaliserProperty
from leon_preset import symmetric_normaliser, symmetric_group
from permutation import Permutation
from partition import Partition
from group import PermGroup

class TestLeonPresets(unittest.TestCase):
    def prop_group_test(self, container, group, prop):        
        for ele in container:
            self.assertEqual(prop.property_check(ele), ele in group)

    def test_symmetric_group(self):
        size = 6
        s6 = symmetric_group(6)
        self.assertEqual(s6.order(), 720)
    
    def test_normaliser(self):
        size = 6
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[1,2]])
        b = cf([[1,2,3,4,5,6]])
        S6 = PermGroup.fixed_base_group([a,b])
        G = PermGroup.fixed_base_group([b])
        norm = symmetric_normaliser(G)
        prop = NormaliserProperty(G)
        self.prop_group_test(S6._list_elements(), norm, prop)
        
    def test_normaliser_large(self):
        size = 10
        cf = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[1,2],[7,10,8]])
        b = cf([[1,2,3,4,5,6],[7,8,9,10]])
        c = cf([[1,7]])
        d = cf([[1,3,7,8,9]])
        e = cf([[9,10]])
        G = PermGroup.fixed_base_group([a,b])
        norm = symmetric_normaliser(G)
        prop = NormaliserProperty(G)
        self.prop_group_test([a,b,c,d,e], norm, prop)        
        

        
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLeonPresets))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())