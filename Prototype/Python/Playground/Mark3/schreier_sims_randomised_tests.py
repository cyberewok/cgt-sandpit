import unittest
from group import PermGroup as Group
from ordering import ordering_to_perm_key, ordering_to_key
from permutation import Permutation
from schreier_sims_randomised import RandomSchreierGenerator

class TestRandomSchreierGenerator(unittest.TestCase):
    
    def test_complete_till_level(self):
        degree = 4
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        s1 = cf([[1,2,3,4]])
        s2 = cf([[1,2]])
        gens = [s1,s2]
        rg = RandomSchreierGenerator(gens)
        rg.complete_till_level(4)
        self.assertEqual(rg.structure.order(), 24)
        #print(rg.structure.schreier_graphs)
        #self.assertEqual(s_g, [s2,identity,s1,s2])    
    
    def test_sift_till_level(self):
        degree = 4
        cf = lambda x:Permutation.read_cycle_form(x, degree)
        s1 = cf([[1,2]])
        s2 = cf([[1,2,3,4]])
        gens = [s1,s2]
        rg = RandomSchreierGenerator(gens)
        rg.sift_till_level(s1,4)
        rg.sift_till_level(cf([]),4)
        #self.assertEqual(s_g, [s2,identity,s1,s2])

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRandomSchreierGenerator))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())