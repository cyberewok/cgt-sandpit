import unittest
from permutation import Permutation
from group import PermDoubleCoset, PermCoset, PermGroup

class TestCoset(unittest.TestCase):
    pass

class TestDoubleCoset(unittest.TestCase):
    
    def test_trivial_double_coset(self):
        G = PermGroup([Permutation([1,2,3,4])])
        a = Permutation([1,3,2,4])
        dcs = G*a*G
        self.assertTrue(a in dcs._list_elements())
        

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
            if g not in H_ele:
                self.assertFalse(g in H)
            if g not in H:
                self.assertFalse(g in H_ele)
    
    def pre_post_works(self, pre, post, G):
        ele = G.prefix_postfix_image_member(pre,post)
        self.assertTrue(ele is not None)
        for i in range(len(post)):
            self.assertEqual(pre[i]**ele, post[i])
        self.assertTrue(ele in G)        
        
    def test_change_base(self):
        cf = Permutation.read_cycle_form
        a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
        b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
        G = PermGroup([a,b])
        G.change_base([1,3])
        self.assertEqual(G.base[:2], [1,3])
        
    def test_change_base_redundancy(self):
        cf = lambda x: Permutation.read_cycle_form(x,6)
        a = cf([[1,2,3,4],[5,6]])
        b = cf([[1,2]])
        G = PermGroup([a,b])
        G.change_base([5,6,1,2,3,4])
        self.assertEqual(G.base[:4],[5,6,1,2])
    
    def test_pre_post_element(self):
        cf = Permutation.read_cycle_form
        a = cf([[2,3],[4,6],[5,8],[9,11]], 13)
        b = cf([[1,2,4,7,9,3,5,6,8,10,11,12,13]], 13)
        G = PermGroup.fixed_base_group([a,b], [1,3])
        pre = [1,3]
        post = [9,3]
        self.pre_post_works(pre, post, G)
    
    def test_pre_post_element_A4(self):
        cf = Permutation.read_cycle_form
        a = cf([[1,2],[3,4]], 5)
        b = cf([[1,2,3]], 5)
        G = PermGroup.fixed_base_group([a,b], [5,4,3,2,1])
        pre = [5,4]
        post = [4,3]
        ele = G.prefix_postfix_image_member(pre,post)
        self.assertTrue(ele is None)
        pre = [5,4,3]
        post = [5,2,1]
        self.pre_post_works(pre, post, G)
        ele = G.prefix_postfix_image_member(pre,post)
        self.assertEqual(cf([[1,3],[2,4]],5),ele)
        
    def test_order(self):
        cf = lambda x : Permutation.read_cycle_form(x,6)
        g1 = cf([[1,4,5,2,3]])
        g2 = cf([[1,2],[3,4]])
        g3 = cf([[1,2],[6,5]])
        G = PermGroup([g1,g2,g3])
        self.assertEqual(G.order(), 360)
        
    def test_degree(self):
        cf = lambda x : Permutation.read_cycle_form(x,6)
        g1 = cf([[1,4,5,2,3]])
        g2 = cf([[1,2],[3,4]])
        g3 = cf([[1,2],[6,5]])
        G = PermGroup([g1,g2,g3])
        self.assertEqual(G.degree, 6)
        cf = lambda x : Permutation.read_cycle_form(x,5)
        g1 = cf([[1,4,5,2,3]])
        g2 = cf([[1,2],[3,4]])
        g3 = cf([[1,2]])
        G = PermGroup([g1,g2,g3])
        self.assertEqual(G.degree, 5)            
    
    def test_empty_initialisation(self):
        s1 = Permutation.read_cycle_form([], 3)
        G = PermGroup([s1])
        self.assertEqual(len(G), 1)
        G = PermGroup([])
        self.assertEqual(len(G), 1)
    
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
        cf = lambda x:Permutation.read_cycle_form(x, 6)
        g1 = cf([[1,2,3,4,5,6]])
        g2 = cf([[1,2]])
        h1 = cf([[3,4,5,6]])
        h2 = cf([[3,4]])
        a1 = cf([[3,1],[6,4]])
        a2 = cf([[1,6,4]])
        G = PermGroup([g1, g2])
        H = PermGroup([h1, h2])
        self.contains_membership_test(G, H)
        S6 = PermGroup.fixed_base_group([g1,g2], [5,2,1,3,4,6])
        A4 = PermGroup.fixed_base_group([a1,a2], [3,1,2,5,6,4])
        self.contains_membership_test(S6, A4)
        
        
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
    
    def test_fixed_base_group(self):
        g1 = Permutation.read_cycle_form([[1,2,3,4,5,6]], 6)
        g2 = Permutation.read_cycle_form([[1,2]], 6)
        h1 = Permutation.read_cycle_form([[3,4,5,6]], 6)
        h2 = Permutation.read_cycle_form([[3,4]], 6)
        G = PermGroup.fixed_base_group([g1, g2], [5,4])
        H = PermGroup.fixed_base_group([h1, h2], [1,2,3,4,5,6])
        N = PermGroup.fixed_base_group([g1,h1], [])
        self.assertEqual(G.base[:2], [5,4])
        self.assertEqual(H.base[:4], [1,2,3,4])
        self.contains_membership_test(G, H)
        
    def test_base_image_member(self):
        h1 = Permutation.read_cycle_form([[3,4,5,6,7]], 7)
        h2 = Permutation.read_cycle_form([[3,4]], 7)
        H = PermGroup.fixed_base_group([h1, h2], [3,4,5,6])
        self.assertEqual(H.base, [3,4,5,6])
        image1 = [1,2,3,4]
        image2 = [5,3,4,6]
        self.assertTrue(H.base_image_member(image1) is None)
        self.assertEqual(H.base_image_member(image2), Permutation.read_cycle_form([[3,5,4]],7))   
    
    def test_orbit(self):
        g1 = Permutation.read_cycle_form([[1,2,3,4]], 4)
        g2 = Permutation.read_cycle_form([[1,2]], 4)
        base = [3,4,1]
        reverse_priority = [3,4,1,2]
        G = PermGroup.fixed_base_group([g1, g2], base)
        self.assertEqual(G.orbit(1), [1,2,3,4])
        self.assertEqual(G.orbit(1, stab_level = 0), [1,2,3,4])
        self.assertEqual(G.orbit(1, stab_level = 1), [1,2,4])
        self.assertEqual(G.orbit(1, stab_level = 2), [1,2])
        self.assertEqual(G.orbit(1, stab_level = 3), [1])
        self.assertEqual(G.orbit(1, key = lambda x : reverse_priority[x - 1]), [3,4,1,2])
    
    def test_orbits(self):
        cf = Permutation.read_cycle_form
        a = cf([[1, 2], [6,7]],7)
        b = cf([[1,2,3,4], [6,7]], 7)
        G=PermGroup.fixed_base_group([a,b], [1,2,3])
        self.assertEqual(sorted(G.orbits()), [[1,2,3,4],[5],[6,7]])
    
    def test_rand_element(self):
        cf = Permutation.read_cycle_form
        a = cf([[1, 2], [6,7]],7)
        b = cf([[1,2,3,4], [6,7]], 7)
        G=PermGroup([a,b])
        for _ in range(100):
            g = G._rand_element()
            self.assertTrue(g in G)
        
        
    
def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDoubleCoset))
    suite.addTest(unittest.makeSuite(TestCoset))
    suite.addTest(unittest.makeSuite(TestGroup))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())