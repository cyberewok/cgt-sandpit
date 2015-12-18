import unittest
from permutation import Permutation
from schreier_sims import schreier_sims_algorithm
from schreier_sims import _coset_rep_inverses, _coset_reps, _coset_rep_inverse
from schreier_sims import _schreier_graph, _schreier_graph_expand
from schreier_sims import _schreier_generators

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
        self.assertEquals(s_g, _coset_rep_inverses(s_g, identity))    

def all_tests_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSchreierSims))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())