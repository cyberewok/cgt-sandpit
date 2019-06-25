import unittest
from cgt.ordering import ordering_to_perm_key, ordering_to_key
from cgt.permutation import Permutation
from cgt.schreier_sims import SchreierSimsGenerator
from cgt.schreier_sims import NaiveSchreierSimsGenerator


class TestNaiveSchreierSimsGenerator(unittest.TestCase):
        
    def test_schreier_sims_algorithm(self):
        cf  =Permutation.read_cycle_form
        a = cf([[1, 2]],4)
        b = cf([[1,2,3,4]], 4)
        c = cf([[2, 3, 4]], 4)
        d = cf([[2, 3],[1,4]], 4)
        e = cf([], 4)
        f = cf([[1, 2, 3]], 4)
        alg = NaiveSchreierSimsGenerator([a,b])
        alg.complete()
        struct = alg.structure
        self.assertTrue(a in struct)
        self.assertTrue(b in struct)        
        self.assertTrue(c in struct)
        self.assertTrue(d in struct)
        self.assertTrue(e in struct)
        self.assertTrue(f in struct)    
        alg = NaiveSchreierSimsGenerator([c,d])
        alg.complete()
        struct = alg.structure
        self.assertFalse(a in struct)
        self.assertFalse(b in struct)
        self.assertTrue(c in struct)
        self.assertTrue(d in struct)
        self.assertTrue(e in struct)
        self.assertTrue(f in struct)
    
    def test_single_schreier_generator(self):
        size = 5
        cf  = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[1, 2, 5, 3, 4]])
        b = cf([[4, 5]])        
        alg = NaiveSchreierSimsGenerator([a,b])
        alg.complete()
        struct = alg.structure
        self.assertEqual(struct.order(), 120)
    
    def test_order_correctness(self):
        size = 5
        cf  = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[1, 4, 2, 3]])
        b = cf([[1, 5], [3, 4]])        
        alg = NaiveSchreierSimsGenerator([a,b])
        alg.complete()
        struct = alg.structure
        self.assertEqual(struct.order(), 120)
        a = cf([[1, 4, 2, 5]])
        b = cf([[1, 3], [4, 5]])        
        alg = NaiveSchreierSimsGenerator([a,b])
        alg.complete()
        struct = alg.structure
        self.assertEqual(struct.order(), 120)

class TestSchreierSimsGenerator(unittest.TestCase):
        
    def test_schreier_sims_algorithm(self):
        cf  =Permutation.read_cycle_form
        a = cf([[1, 2]],4)
        b = cf([[1,2,3,4]], 4)
        c = cf([[2, 3, 4]], 4)
        d = cf([[2, 3],[1,4]], 4)
        e = cf([], 4)
        f = cf([[1, 2, 3]], 4)
        alg = SchreierSimsGenerator([a,b])
        alg.complete()
        struct = alg.structure
        self.assertTrue(a in struct)
        self.assertTrue(b in struct)        
        self.assertTrue(c in struct)
        self.assertTrue(d in struct)
        self.assertTrue(e in struct)
        self.assertTrue(f in struct)    
        alg = SchreierSimsGenerator([c,d])
        alg.complete()
        struct = alg.structure
        self.assertFalse(a in struct)
        self.assertFalse(b in struct)
        self.assertTrue(c in struct)
        self.assertTrue(d in struct)
        self.assertTrue(e in struct)
        self.assertTrue(f in struct)
    
    def test_single_schreier_generator(self):
        size = 5
        cf  = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[1, 2, 5, 3, 4]])
        b = cf([[4, 5]])        
        alg = SchreierSimsGenerator([a,b])
        alg.complete()
        struct = alg.structure
        self.assertEqual(struct.order(), 120)
    
    def test_order_correctness(self):
        size = 5
        cf  = lambda x: Permutation.read_cycle_form(x, size)
        a = cf([[1, 4, 2, 3]])
        b = cf([[1, 5], [3, 4]])        
        alg = SchreierSimsGenerator([a,b])
        #OFFENDING LINE
        alg.complete()
        struct = alg.structure        
        self.assertEqual(struct.order(), 120)
        a = cf([[1, 4, 2, 5]])
        b = cf([[1, 3], [4, 5]])        
        alg = SchreierSimsGenerator([a,b])
        alg.complete()
        struct = alg.structure
        self.assertEqual(struct.order(), 120)

def all_tests_suite():
    suite = unittest.TestSuite()    
    suite.addTest(unittest.makeSuite(TestSchreierSimsGenerator))
    suite.addTest(unittest.makeSuite(TestNaiveSchreierSimsGenerator))
    return suite

if __name__ == '__main__':
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(all_tests_suite())