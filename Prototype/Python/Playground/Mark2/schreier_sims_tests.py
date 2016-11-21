import unittest
from ordering import ordering_to_perm_key, ordering_to_key
from permutation import Permutation
from schreier_sims import schreier_sims_algorithm, schreier_sims_algorithm_fixed_base, naive_schreier_sims_algorithm
from schreier_sims import membership_siftee, base_image_member
from schreier_sims import _coset_rep_inverses, _coset_reps, _coset_rep_inverse
from schreier_sims import _schreier_graph, _schreier_graph_expand
from schreier_sims import _schreier_generators
from schreier_sims import group_size, element_at_index, membership_index

class TestSchreierSims(unittest.TestCase):
    def coset_construction_from_schreier_tree_test(self, gens):
        identity = gens[0] * gens[0]**-1
        base, strong_gens, chain_generators, schreier_graphs = schreier_sims_algorithm(gens, identity)
        no_errors = True
        for s_g in schreier_graphs[0:-1]:
            coset_inverses_1 = _coset_rep_inverses(s_g, identity)
            coset_inverses_2 = [_coset_rep_inverse(i + 1, s_g, identity) for i in range(len(identity))]
            if coset_inverses_1 != coset_inverses_2:
                no_errors = False
                print(coset_inverses_1)
                print(coset_inverses_2)
        self.assertTrue(no_errors)
        
    def test_coset_constructions(self):    
        s1 = Permutation.read_cycle_form([[2,3,5,7]], 8)
        s2 = Permutation.read_cycle_form([[1,2,4,8]], 8)
        self.coset_construction_from_schreier_tree_test([s1, s2])   
             
    def test_schreier_graph_construction(self):
        s1 = Permutation.read_cycle_form([[2,3]], 4)
        s2 = Permutation.read_cycle_form([[1,2,4]], 4)
        gens = [s1,s2]
        identity = Permutation([1,2,3,4])
        s_g = _schreier_graph(2, gens, identity)
        self.assertEqual(s_g, [s2,identity,s1,s2])
        
    def test_coset_reps(self):
        s1 = Permutation.read_cycle_form([[2,3]], 4)
        s2 = Permutation.read_cycle_form([[1,2,4]], 4)
        gens = [s1,s2]
        identity = Permutation([1,2,3,4])
        s_g = _schreier_graph(2, gens, identity)
        cosets = _coset_reps(s_g, identity)
        self.assertEqual(cosets, [Permutation.read_cycle_form([[1,4,2]], 4),identity,s1,s2])

    def test_schreier_generators(self):
        s1 = Permutation.read_cycle_form([[2,3]], 4)
        s2 = Permutation.read_cycle_form([[1,2,4]], 4)
        gens = [s1,s2]
        identity = Permutation([1,2,3,4])
        s_g = _schreier_graph(2, gens, identity)
        cosets = _coset_reps(s_g, identity)
        s_gen = _schreier_generators(2, cosets, gens, identity)
        gen_1 = Permutation.read_cycle_form([[3,4]], 4)
        gen_2 = Permutation.read_cycle_form([[1,3,4]], 4)
        gen_3 = Permutation.read_cycle_form([[1,3]], 4)
        self.assertEqual(s_gen, [gen_1, gen_2, gen_3])
        
    def test_coset_rep_inverses(self):
        identity = Permutation([1,2,3,4])
        b = Permutation([3,2,1,4])
        s_g = [identity,None,b,None]
        self.assertEqual(s_g, _coset_rep_inverses(s_g, identity))
    
    def test_base_image_member(self):
        cf  =Permutation.read_cycle_form
        a = cf([[1, 2]],4)
        b = cf([[1,2,3,4]], 4)
        c = cf([[2,3]], 4)
        e = cf([],4)
        base, gens, c_gens, graphs = schreier_sims_algorithm_fixed_base([a,b],[1,2,3,4], e)
        self.assertEqual(base_image_member(base,[1,3,2],graphs,e), c)
    
    def test_group_size(self):
        cf  = Permutation.read_cycle_form
        a = cf([[1, 2, 3,4,5]],5)
        b = cf([[1,2,3]], 5)
        e = cf([],5)
        base, _, _, graphs = schreier_sims_algorithm_fixed_base([a,b],[1,2,3,4,5], e)
        self.assertEqual(group_size(graphs),60)
    
    def test_element_at_index(self):
        cf  = Permutation.read_cycle_form
        a = cf([[1, 2, 3,4,5]],5)
        b = cf([[1,2,3]], 5)
        e = cf([],5)
        ordering = [3,5,2,1,4]
        base, _, _, graphs = schreier_sims_algorithm_fixed_base([a,b], ordering, e)
        full_group = []
        ele_key = ordering_to_key(ordering)        
        perm_key = ordering_to_perm_key(ordering)
        for index in range(group_size(graphs)):
            full_group.append(element_at_index(base, graphs, index, e, key=ele_key))
        ordered_group = sorted(full_group, key = perm_key)
        #for x,y in zip(full_group, ordered_group):
            #print("{!s:<20} {!s:<20}".format(x,y))
        self.assertEqual(full_group, ordered_group)
        
    
    def test_memebership_index(self):
        cf  = Permutation.read_cycle_form
        a = cf([[1, 2, 3,4,5]],5)
        b = cf([[1,2,3]], 5)
        c = cf([[1,2]], 5)
        e = cf([],5)
        ordering = [3,5,2,1,4]
        base, _, _, graphs = schreier_sims_algorithm_fixed_base([a,b], ordering, e)
        S5_base, _, _, S5_graphs = schreier_sims_algorithm_fixed_base([a,c], ordering, e)
        real_group = []
        S5_group = []
        
        ele_key = ordering_to_key(ordering)        
        perm_key = ordering_to_perm_key(ordering)
        
        for index in range(group_size(S5_graphs)):
            S5_group.append(element_at_index(S5_base, S5_graphs, index, e, key=ele_key))
         
        self.assertEquals(len(S5_group), 120)
        self.assertEquals(S5_group, sorted(S5_group, key = perm_key))
        
        
        for index in range(group_size(graphs)):
            real_group.append(element_at_index(base, graphs, index, e, key=ele_key))
             
        self.assertEquals(len(real_group), 60)
        self.assertEquals(real_group, sorted(real_group, key = perm_key))
        
        for ele in S5_group:
            cand_index = membership_index(ele, graphs, base, e, key = ele_key)
            if cand_index > -1:
                #print("{}: {} {}?".format(cand_index, ele, real_group[cand_index]))
                self.assertTrue(ele in real_group)
                self.assertEquals(real_group[cand_index], ele)
            else:
                self.assertFalse(ele in real_group)
        
        
    
    def test_schreier_sims_algorithm(self):
        cf  =Permutation.read_cycle_form
        a = cf([[1, 2]],4)
        b = cf([[1,2,3,4]], 4)
        c = cf([[2, 3, 4]], 4)
        d = cf([[2, 3]], 4)
        e = cf([], 4)
        info = schreier_sims_algorithm([], e)
        self.assertEquals(info, ([],[],[],[]))
        info = schreier_sims_algorithm([e,e,e,e], e)
        self.assertEquals(info, ([],[],[],[]))
        base, gens, c_gens, graphs = schreier_sims_algorithm([a,b], e)
        self.assertEquals(len(base), 3)
        
    def test_naive_schreier_sims_algorithm(self):
        cf  =Permutation.read_cycle_form
        a = cf([[1, 2]],4)
        b = cf([[1,2,3,4]], 4)
        c = cf([[2, 3, 4]], 4)
        d = cf([[2, 3],[1,4]], 4)
        e = cf([], 4)
        info = naive_schreier_sims_algorithm([], e)
        self.assertEquals(info, ([],[],[],[]))
        info = naive_schreier_sims_algorithm([e,e,e,e], e)
        self.assertEquals(info, ([],[],[],[]))
        base, gens, c_gens, graphs = naive_schreier_sims_algorithm([c,d], e)
        self.assertEquals(len(base), 2)
        siftee = membership_siftee(a, graphs, base, e)
        self.assertNotEqual(siftee, e)
        siftee = membership_siftee(cf([[1,2,3]],4), graphs, base, e)
        self.assertEqual(siftee, e)        
        
        
    def test_schreier_sims_algorithm_fixed_base(self):
        cf  =Permutation.read_cycle_form
        a = cf([[1, 2]],4)
        b = cf([[1,2,3,4]], 4)
        c = cf([[2, 3, 4]], 4)
        d = cf([[2, 3], [1,4]], 4)
        e = cf([], 4)
        info = schreier_sims_algorithm_fixed_base([], [1,2,3,4], e)
        self.assertEquals(info, ([],[],[],[]))
        info = schreier_sims_algorithm_fixed_base([e,e,e,e], [1,2,3,4], e)
        self.assertEquals(info, ([],[],[],[]))
        base, gens, c_gens, graphs = schreier_sims_algorithm_fixed_base([a,b], [4,3], e)
        self.assertEquals(len(base), 3)
        self.assertEquals(base[:2], [4,3])
        base, gens, c_gens, graphs = schreier_sims_algorithm_fixed_base([c,d], [4,1], e)
        self.assertEquals(base[:2], [4,1])
        siftee = membership_siftee(a, graphs, base, e)
        self.assertNotEqual(siftee, e)
        siftee = membership_siftee(cf([[1,2,3]],4), graphs, base, e)
        self.assertEqual(siftee, e)
        base, gens, c_gens, graphs = schreier_sims_algorithm_fixed_base([c], [1,2,3,4], e)
        self.assertEquals(base[:2], [1,2])
        siftee = membership_siftee(a, graphs, base, e)
        self.assertNotEqual(siftee, e)
        siftee = membership_siftee(cf([[2,4,3]],4), graphs, base, e)
        self.assertEqual(siftee, e)        

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSchreierSims))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())