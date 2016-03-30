import unittest
from permutation import Permutation
from group import PermCoset, PermGroup

class TestCoset(unittest.TestCase):
    pass

class TestGroup(unittest.TestCase):
 
    def contains_membership_test(self, group, subgroup):
        G = group
        H = subgroup
        G_ele = G._list_elements()
        H_ele = H._list_elements()
        for g in G_ele:
            self.assertTrue(g in G)
            if g in H_ele:
                self.assertTrue(g in H)
            if g in H:
                self.assertTrue(g in H_ele)  
    
    def test_initialisation(self):
        s1 = Permutation.read_cycle_form([[2,3,5,7],[9, 10]], 10)
        s2 = Permutation.read_cycle_form([[1,2,4,8],[9, 10]], 10)
        G = PermGroup([s1, s2])
        base_gen_pairs = list(zip(['_']+G.base, G.chain_generators))
        prev = base_gen_pairs[0][1]
        base_eles = []
        for base_ele, gens in base_gen_pairs[1:-1]:
            base_eles.append(base_ele)
            for g in gens:
                for b in base_eles:
                    self.assertEqual(b, b**g)
            temp = PermGroup(gens)
            self.assertTrue(len([g for g in prev if g not in temp])>0)
            prev = gens   
    
    def test_len(self):
        s1 = Permutation.read_cycle_form([[1,2,3,4]], 4)
        s2 = Permutation.read_cycle_form([[1,2]], 4)
        G = PermGroup([s1, s2])
        self.assertEqual(len(G), len(G._list_elements()))
        self.assertEqual(len(G), 24)
        self.assertTrue(Permutation.read_cycle_form([[3,4]], 4) in G._list_elements())
        
    def test_coset(self):
        g1 = Permutation.read_cycle_form([[1,2,3,4]], 4)
        g2 = Permutation.read_cycle_form([[1,2]], 4)
        h1 = Permutation.read_cycle_form([[1,2,3]], 4)
        h2 = Permutation.read_cycle_form([[1,2]], 4)
        G = PermGroup([g1, g2])
        H = PermGroup([h1, h2])
        coset = sorted((H*g1)._list_elements())
        for c in coset:
            self.assertEqual(sorted((H*c)._list_elements()), coset)
        self.assertEqual(len(H), len(coset))
        coset = sorted((g1*H)._list_elements())   
        for c in coset:
            self.assertEqual(sorted((c*H)._list_elements()), coset)
        self.assertEqual(len(H), len(coset))
    
    def test_contains(self):
        g1 = Permutation.read_cycle_form([[1,2,3,4,5,6,7]], 7)
        g2 = Permutation.read_cycle_form([[1,2]], 7)
        h1 = Permutation.read_cycle_form([[3,4,5,6,7]], 7)
        h2 = Permutation.read_cycle_form([[3,4]], 7)
        G = PermGroup([g1, g2])
        H = PermGroup([h1, h2])
        self.contains_membership_test(G, H)
    
    def test_coset_enumeration(self):
        g1 = Permutation.read_cycle_form([[1,2,3,4]], 4)
        g2 = Permutation.read_cycle_form([[1,2]], 4)
        h1 = Permutation.read_cycle_form([[1,2,3]], 4)
        h2 = Permutation.read_cycle_form([[1,2]], 4)
        G = PermGroup([g1, g2])
        H = PermGroup([h1, h2])
        cosets = G._left_cosets(H)
        total = 0
        elements = []
        for coset in cosets:
            temp_eles = coset._list_elements()
            elements += temp_eles
            self.assertEqual(len(temp_eles),len(H))
            total += len(temp_eles)
        self.assertEqual(len(G), total)
        self.assertEqual(sorted(G._list_elements()), sorted(elements))        
        cosets = G._right_cosets(H)
        total = 0
        elements = []
        for coset in cosets:
            temp_eles = coset._list_elements()
            elements += temp_eles
            self.assertEqual(len(temp_eles),len(H))
            total += len(temp_eles)
        self.assertEqual(len(G), total)
        self.assertEqual(sorted(G._list_elements()), sorted(elements))
    
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCoset))
    suite.addTest(unittest.makeSuite(TestGroup))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())